"""IPC-PyMDE: Minimum-Distortion Embedding Network Layout

This module implements a IPC Network Layout to be used with PyMDE[1].
The IPC layout grants a non-blocking behavior for PyMDE.
PyMDE solves minimum-distortion embedding problem using pytorch.

References
----------
    [1] A. Agrawal, A. Ali, and S. Boyd, “Minimum-Distortion Embedding,”
    arXiv:2103.02559 [cs, math, stat], Mar. 2021, Accessed: Jul. 24, 2021.
    `http://arxiv.org/abs/2103.02559 <http://arxiv.org/abs/2103.02559>`_

Notes
-----
    Python 3.8 or greater is a requirement for this module.


Attributes
----------
_CONSTRAINTS : dict
_PENALTIES : dict

"""
import numpy as np
import torch
import pymde

from helios.layouts.base import NetworkLayoutIPCRender
from helios.layouts.base import NetworkLayoutIPCServerCalc


_CONSTRAINTS = {
    'centered': pymde.Centered,
    'standardized': pymde.Standardized,
    'anchored': pymde.Anchored
}

_PENALTIES = {
    'cubic': pymde.penalties.Cubic,
    'huber': pymde.penalties.Huber,
    'invpower': pymde.penalties.InvPower,
    'linear': pymde.penalties.Linear,
    'log': pymde.penalties.Log,
    'log1p': pymde.penalties.Log1p,
    'logratio': pymde.penalties.LogRatio,
    'logistic': pymde.penalties.Logistic,
    'power': pymde.penalties.Power,
    'pushandpull': pymde.penalties.PushAndPull,
    'quadratic': pymde.penalties.Quadratic,
}


class MDEServerCalc(NetworkLayoutIPCServerCalc):
    def __init__(
        self,
        edges_buffer_name,
        positions_buffer_name,
        info_buffer_name,
        weights_buffer_name=None,
        snapshots_buffer_name=None,
        penalty_name=None,
        penalty_parameters_buffer_name=None,
        attractive_penalty_name='log1p',
        repulsive_penalty_name='log',
        use_shortest_path=False,
        constraint_name=None,
        constraint_anchors_buffer_name=None,
    ):
        """This Obj. reads the network information stored in a shared memory
        resource and execute the MDE layout algorithm

        Parameters
        -----------
        edges_buffer_name : str
        positions_buffer_name : str
        info_buffer_name : str
        weights_buffer_name : str, optional
        snapshots_buffer_name : str, optional
        penalty_name : str, optional
        penalty_parameters_buffer_name : str, optional
        attractive_penalty_name : str, optional
        repulsive_penalty_name : str, optional
        use_shortest_path : str, optional
        constraint_name : str, optional
        constraint_anchors_buffer_name : str, optional

        """
        super().__init__(
            edges_buffer_name,
            positions_buffer_name,
            info_buffer_name,
            weights_buffer_name,
            snapshots_buffer_name,
        )
        self._positions_torch = torch.tensor(
            self._shm_manager.positions.data)
        
        edges_torch = torch.tensor(
            self._shm_manager.edges.data)
        if weights_buffer_name is not None:
            weights_torch = torch.tensor(
                self._shm_manager.weights.data)
        else:
            weights_torch = torch.ones(edges_torch.shape[0])
        if use_shortest_path and penalty_name is None:
            g_torch = pymde.Graph.from_edges(edges_torch, weights_torch)
            shortest_paths_graph = pymde.preprocess.graph.shortest_paths(
                g_torch)
            edges_torch = shortest_paths_graph.edges
            distortion = pymde.losses.WeightedQuadratic(
                shortest_paths_graph.distances)
        elif penalty_name is None:
            distortion = pymde.losses.WeightedQuadratic(weights_torch)
        else:
            if penalty_name in _PENALTIES.keys():
                func = _PENALTIES[penalty_name]
                if penalty_name == 'pushandpull':
                    if attractive_penalty_name not in _PENALTIES.keys() or\
                         repulsive_penalty_name not in _PENALTIES.keys():
                        raise ValueError(
                            'The attractive/repulsive penalty' +
                            f' valid names are: {list(_PENALTIES.keys())}')
                    distortion = func(
                        weights_torch,
                        _PENALTIES[attractive_penalty_name],
                        _PENALTIES[repulsive_penalty_name])
                if penalty_parameters_buffer_name is not None:
                    self._shm_manager.load_array(
                        'penalty_parameters',
                        penalty_parameters_buffer_name,
                        'float32',
                    )
                    distortion = func(
                        weights_torch,
                        *self._shm_manager.penalty_parameters.data)
                else:
                    distortion = func(weights_torch)
            else:
                raise ValueError(
                    'The penalties available are: ' +
                    f'{list(_PENALTIES.keys())}')
        if constraint_name is None:
            constraint = None
        else:
            if constraint_name in _CONSTRAINTS.keys():
                if constraint_name == 'anchored':
                    if constraint_anchors_buffer_name is None:
                        raise ValueError(
                            'Missing constraint anchors ' +
                            'buffer name')
                    self._shm_manager.load_array(
                        'anchors',
                        constraint_anchors_buffer_name,
                        'float32',
                    )
                    num_anchors = self._shm_manager.anchors._num_rows
                    torch_anchors = torch.tensor(
                        self._shm_manager.anchors._repr[
                            0:num_anchors, self._dimension].astype('int64')
                    )
                    torch_anchors_pos = torch.tensor(
                        self._shm_manager.anchors._repr[
                            0:num_anchors, 0:self._dimension]
                    )

                    constraint = pymde.Anchored(
                        anchors=torch_anchors, values=torch_anchors_pos)
                else:
                    constraint = _CONSTRAINTS[constraint_name]()

            else:
                raise ValueError(
                    'The constraint valid names are: ' +
                    f'{list(_CONSTRAINTS.keys())}')
        self.mde = pymde.MDE(
           self._shm_manager.positions._repr.shape[0],
           self._dimension,
           edges_torch,
           distortion_function=distortion,
           constraint=constraint
        )

    def start(self, steps=100, iters_by_step=3):
        """This method starts the network layout algorithm.

        Parameters
        ----------
        steps : int
            number of iterations
        iters_by_step: int
            number of iterations per step

        """
        # -1 means the computation has been intialized
        self._shm_manager.info._repr[1] = -1
        for step in range(steps):
            self._positions_torch = self.mde.embed(
                    self._positions_torch,
                    max_iter=iters_by_step)

            self._update(self._positions_torch.cpu().numpy(), step)
        # to inform that everthing worked
        self._shm_manager.info._repr[1] = 1


class MDE(NetworkLayoutIPCRender):
    """Minimum Distortion Embedding algorithm running on IPC 

    This call  the PyMDE lib running in a different process which comunicates
    with this object through SharedMemory from python>=3.8.

    References
    ----------
    [1] A. Agrawal, A. Ali, and S. Boyd, “Minimum-Distortion Embedding,”
    arXiv:2103.02559 [cs, math, stat], Mar. 2021, Accessed: Jul. 24, 2021.
    `http://arxiv.org/abs/2103.02559 <http://arxiv.org/abs/2103.02559>`_

    Notes
    -----
    Python 3.8+ is required to use this

    """
    def __init__(
        self,
        edges,
        network_draw,
        weights=None,
        use_shortest_path=True,
        constraint_name=None,
        anchors=None,
        anchors_pos=None,
        penalty_name=None,
        penalty_parameters=None,
        attractive_penalty_name='log1p',
        repulsive_penalty_name='log',
    ):
        """

        Parameters
        -----------
        edges : ndarray
            the edges of the graph. A numpy array of shape (n_edges, 2)
        network_draw : NetworkDraw
            a NetworkDraw object
        weights: array, optional
            edge weights. A one dimensional array of shape (n_edges, )
        use_shortest_path : bool, optional
            If set to True, shortest path is used to compute the layout
        constraint_name : str, optional
            centered, standardized or anchored
        anchors : array, optional
            a list of vertex that will be anchored
        anchors_pos : ndarray, optional
            The positions of the anchored vertex
        penalty_name : str, optional
            cubic, huber, invpower, linear, log, log1p, logratio,
            logistic, power, pushandpull  or quadratic
        penalty_parameters : array, optional
            the parameters of the penalty function
        attractive_penalty_name : str, optional
            cubic, huber, invpower, linear, log, log1p, logratio,
            logistic, power, pushandpull  or quadratic
        repulsive_penalty_name : str, optional
            cubic, huber, invpower, linear, log, log1p, logratio,
            logistic, power, pushandpull  or quadratic

        """
        super().__init__(
            network_draw,
            edges,
            weights,
        )

        if constraint_name not in _CONSTRAINTS.keys() and\
                constraint_name is not None:
            raise ValueError(
                'The constraint valid names are: ' +
                f'{list(_CONSTRAINTS.keys())}')
        if constraint_name == 'anchored':
            if anchors is None or anchors_pos is None:
                raise ValueError(
                    '"anchors" and "anchors_pos" are mandatory ' +
                    'when using anchored constraint')

            self._shm_manager.add_array(
                'anchors',
                data=np.c_[anchors_pos, anchors],
                dtype='float32'
            )

        self._constraint_name = constraint_name
        for penalty in [
                penalty_name, attractive_penalty_name,
                repulsive_penalty_name]:
            if penalty not in _PENALTIES.keys() and penalty is not None:
                raise ValueError(
                    'The penalties available are: ' +
                    f'{list(_PENALTIES.keys())}')

        self._penalty_name = penalty_name
        self._attractive_penalty_name = attractive_penalty_name
        self._repulsive_penalty_name = repulsive_penalty_name
        self._use_shortest_path = use_shortest_path

        if isinstance(penalty_parameters, list):
            self._penalty_parameters = penalty_parameters
            self._shm_manager.add_array(
                'penalty_parameters',
                np.array(penalty_parameters),
                dtype='float32'
            )
        else:
            self._penalty_parameters = None

    def _command_string(
            self, steps=100, iters_by_step=3,):
        """This will return the python code which starts the MDEServer

        Parameters
        ----------
        steps : int, optional, default 100
            number of iterations
        iters_by_step : int, optional, default 3
            number of iterations per step

        Returns
        -------
        s : str
            the python code to start the MDEServer

        """
        s = 'from helios.layouts.mde import MDEServerCalc;'
        s += 'from fury.stream.tools import remove_shm_from_resource_tracker;'
        s += 'remove_shm_from_resource_tracker();'
        s += 'mde_h = MDEServerCalc('
        s += f'edges_buffer_name="{self._shm_manager.edges._buffer_name}",'
        s += 'positions_buffer_name='
        s += f'"{self._shm_manager.positions._buffer_name}",'
        s += f'info_buffer_name="{self._shm_manager.info._buffer_name}",'
        if 'weights' in self._shm_manager._shm_attr_names:
            s += 'weights_buffer_name='
            s += f'"{self._shm_manager.weights._buffer_name}",'

        if self._record_positions:
            s += 'snapshots_buffer_name='
            s += f'"{self._shm_manager.snapshots_positions._buffer_name}",'
        s += f'use_shortest_path={self._use_shortest_path},'
        if self._constraint_name is not None:
            s += f'constraint_name="{self._constraint_name}",'
            if self._constraint_name == 'anchored':
                s += 'constraint_anchors_buffer_name='
                s += f'"{self._shm_manager.anchors._buffer_name}",'

        if self._penalty_name is not None:
            s += f'penalty_name="{self._penalty_name}",'

        if self._penalty_name == 'pushandpull':
            s += f'attractive_penalty_name="{self._attractive_penalty_name}",'
            s += f'repulsive_penalty_name="{self._repulsive_penalty_name}",'

        if self._penalty_parameters is not None:
            s += 'penalty_parameters_buffer_name='
            s += f'"{self._shm_manager.penalty_parameters._buffer_name}",'
        s += ');'
        s += f'mde_h.start({steps},{iters_by_step});'
        return s
