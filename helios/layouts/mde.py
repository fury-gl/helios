import numpy as np 
import torch
import pymde

from helios.layouts.base import NetworkLayoutIPCRender
from helios.layouts.base import NetworkLayoutIPCServerCalc


_CONSTRAINTS = {
    'centered': pymde.Centered,
    'standardized': pymde.Standardized,
    # 'anchored': pymde.Anchored
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
    # 'pushandpull': pymde.penalties.PushAndPull,
    'quadratic': pymde.penalties.Quadratic,
}


class MDEServerCalc(NetworkLayoutIPCServerCalc):
    def __init__(
        self,
        edges_buffer_name,
        positions_buffer_name,
        info_buffer_name,
        weights_buffer_name=None,
        dimension=3,
        penalty_name=None,
        use_shortest_path=False,
        constraint_name=None,
        penalty_parameters_buffer_name=None,
    ):
        super().__init__(
            edges_buffer_name,
            positions_buffer_name,
            info_buffer_name,
            weights_buffer_name,
            dimension,
        )
        self._positions_torch = torch.tensor(
            self._shm_manager.positions._repr)
        edges_torch = torch.tensor(
            self._shm_manager.edges._repr)
        if weights_buffer_name is not None:
            weights_torch = torch.tensor(self._shm_manager.weights._repr)
        else:
            weights_torch = torch.ones(edges_torch.shape[0])
        if use_shortest_path:
            g_torch = pymde.Graph.from_edges(edges_torch, weights_torch)
            shortest_paths_graph = pymde.preprocess.graph.shortest_paths(
                g_torch)

            edges_torch = shortest_paths_graph.edges
            distortion = pymde.losses.WeightedQuadratic(
                shortest_paths_graph.distances)
        elif penalty_name is None:
            distortion = pymde.penalties.Quadratic(weights_torch)
        else:
            if penalty_name in _PENALTIES.keys():
                func = distortion = _PENALTIES[penalty_name]
                if penalty_parameters_buffer_name is not None:
                    self._shm_manager.load_array(
                        'penalty_parameters',
                        penalty_parameters_buffer_name,
                        1,
                        'float32'
                    )
                    func(
                        weights_torch,
                        *self._shm_manager.penalty_parameters._repr)
                else:
                    distortion = func(weights_torch)
            else:
                raise ValueError(
                    'The penalties valid names are: ' +
                    f'{list(_PENALTIES.keys())}')
        if constraint_name is None:
            constraint = None
        else:
            if constraint_name in _CONSTRAINTS.keys():
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
        for i in range(steps):
            if i == 0:
                self._positions_torch = self.mde.embed(
                    self._positions_torch,
                    max_iter=iters_by_step)
            else:
                self._positions_torch = self.mde.embed(
                    self._positions_torch, max_iter=iters_by_step)
            self._update(self._positions_torch.cpu().numpy())
        # to inform that everthing worked
        self._shm_manager.info._repr[1] = 1


class MDE(NetworkLayoutIPCRender):
    def __init__(
        self,
        edges,
        network_draw,
        weights=None,
        use_shortest_path=True,
        constraint_name=None,
        penalty_name=None,
        penalty_parameters=None
    ):

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

        self._constraint_name = constraint_name
        self._penalty_name = penalty_name
        self._use_shortest_path = use_shortest_path
        if isinstance(penalty_parameters, list):
            self._penalty_parameters = penalty_parameters
            self._shm_manager.add_array(
                'penalty_parameters',
                np.array(penalty_parameters),
                dimension=1,
                dtype='float32'
            )
        else:
            self._penalty_parameters = None

        self._update()

    def _command_string(
            self, steps=100, iters_by_step=3,):
        s = 'from helios.layouts.mde import MDEServerCalc;'
        s += 'from fury.stream.tools import remove_shm_from_resource_tracker;'
        s += 'remove_shm_from_resource_tracker();'
        s += 'mde_h = MDEServerCalc('
        s += f'edges_buffer_name="{self._shm_manager.edges._buffer_name}",'
        s += f'positions_buffer_name="{self._shm_manager.positions._buffer_name}",'
        s += f'info_buffer_name="{self._shm_manager.info._buffer_name}",'
        s += f'use_shortest_path={self._use_shortest_path},'
        if self._constraint_name is not None:
            s += f'constraint_name="{self._constraint_name}",'
        if self._penalty_name is not None:
            s += f'penalty_name="{self._penalty_name}",'
        if self._penalty_parameters is not None:
            s += 'penalty_parameters_buffer_name='
            s += f'"{self._shm_manager.penalty_parameters._buffer_name}",'
        s += f'dimension={self._dimension});'
        s += f'mde_h.start({steps},{iters_by_step});'
        s += 'mde_h.cleanup();'

        return s
