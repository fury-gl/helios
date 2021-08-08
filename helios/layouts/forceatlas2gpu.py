"""IPC-ForceAtlas2: Network Layout using cuGraph

ForceAtlas2 layout algorithm through IPC using cuGraph.

"""

import numpy as np

try:
    import cudf
    import cugraph as cg
    CUDF_AVAILABLE = True
except ImportError:
    CUDF_AVAILABLE = False

from helios.layouts.base import NetworkLayoutIPCRender
from helios.layouts.base import NetworkLayoutIPCServerCalc


class ForceAtlas2ServerCalc(NetworkLayoutIPCServerCalc):
    """This Obj. reads the network information stored in a shared memory
        resource and execute the ForceAtlas2 layout algorithm

    """
    def __init__(
        self,
        edges_buffer_name,
        positions_buffer_name,
        info_buffer_name,
        weights_buffer_name=None,
        snapshots_buffer_name=None,
        lin_log_mode=False,
        edge_weight_influence=1.0,
        jitter_tolerance=1.0,
        barnes_hut_optimize=True,
        barnes_hut_theta=1.0,
        scaling_ratio=2.0,
        strong_gravity_mode=False,
        gravity=1.0,
    ):
        """

        Parameters
        -----------
        edges_buffer_name : str
            The name of the shared memory buffer where the edges are stored
        positions_buffer_name : str
            The name of the shared memory buffer where the positions are
            stored.
        info_buffer_name : str
        weights_buffer_name : str, optional
        snapshots_buffer_name : str, optional
        lin_log_mode : bool, default False
        edge_weight_influence : float, default 1.0
        jitter_tolerance : float, default 1.0
        barnes_hut_optimize : bool, default True
        barnes_hut_theta : float, default 1.0
        scaling_ratio : float, default 2.0
        strong_gravity_mode : bool, default False
        gravity : float, default 1.0

        """
        super().__init__(
            edges_buffer_name,
            positions_buffer_name,
            info_buffer_name,
            weights_buffer_name,
            snapshots_buffer_name,
        )
        self._vertex = np.arange(0, self._shm_manager.positions._repr.shape[0])

        self._pos_cudf = cudf.DataFrame(
            np.c_[self._shm_manager.positions._repr, self._vertex],
            columns=['x', 'y', 'vertex']
        )
        if weights_buffer_name is not None:
            df = cudf.DataFrame(
                np.c_[
                    self._shm_manager.edges._repr,
                    self._shm_manager.weights._repr
                ],
                columns=['source', 'destination', 'weight'])
            self._G = cg.Graph()
            self._G.from_cudf_edgelist(df, edge_attr='weight')
        else:
            df = cudf.DataFrame(
                self._shm_manager.edges._repr,
                columns=['source', 'destination'])
            self._G = cg.Graph()

            self._G.from_cudf_edgelist(df)

        self.lin_log_mode = lin_log_mode
        self.edge_weight_influence = edge_weight_influence
        self.jitter_tolerance = jitter_tolerance
        self.barnes_hut_optimize = barnes_hut_optimize
        self.barnes_hut_theta = barnes_hut_theta
        self.scaling_ratio = scaling_ratio
        self.strong_gravity_mode = strong_gravity_mode
        self.gravity = gravity

    def start(self, steps=100, iters_by_step=3):
        # -1 means the computation has been intialized
        self._shm_manager.info._repr[1] = -1
        for step in range(steps):
            self._pos_cudf = cg.layout.force_atlas2(
                self._G,
                max_iter=iters_by_step,
                pos_list=self._pos_cudf,
                outbound_attraction_distribution=True,
                lin_log_mode=self.lin_log_mode,
                edge_weight_influence=self.edge_weight_influence,
                jitter_tolerance=self.jitter_tolerance,
                barnes_hut_optimize=self.barnes_hut_optimize,
                barnes_hut_theta=self.barnes_hut_theta,
                scaling_ratio=self.scaling_raio,
                strong_gravity_mode=self.strong_gravity_mode,
                gravity=self.gravity,
                verbose=False,
                callback=None)

            self._update(
                self._pos_cudf.to_pandas().to_numpy()[:, 0:2], step)
        # to inform that everthing worked
        self._shm_manager.info._repr[1] = 1


class ForceAtlas2(NetworkLayoutIPCRender):
    """Performs the ForceAtlas2 algorithm using the cugraph lib.

    The ForceAtlas will be called inside of a different process which
    comunicates with this object through the SharedMemory

    Notes
    -----
    Python 3.8+ is required to use this

    """
    def __init__(
        self,
        edges,
        network_draw,
        weights=None,
        lin_log_mode=False,
        edge_weight_influence=1.0,
        jitter_tolerance=1.0,
        barnes_hut_optimize=True,
        barnes_hut_theta=1.0,
        scaling_ratio=2.0,
        strong_gravity_mode=False,
        gravity=1.0,
    ):
        """

        Parameters
        -----------
        edges : ndarray
        network_draw : NetworkDraw
        weights: array, optional
            edge weights
        lin_log_mode : bool, default False
        edge_weight_influence : float, default 1.0
        jitter_tolerance : float, default 1.0
        barnes_hut_optimize : bool, default True
        barnes_hut_theta : float, default 1.0
        scaling_ratio : float, default 2.0
        strong_gravity_mode : bool, default False
        gravity : float, default 1.0

        """

        super().__init__(
            network_draw,
            edges,
            weights,
        )
        if not network_draw._is_2d:
            raise ValueError('ForceAtlas2 only works for 2d layouts')

        if not CUDF_AVAILABLE:
            raise ImportError(' You need to install cugraph and cudf first')

        self.lin_log_mode = lin_log_mode
        self.edge_weight_influence = edge_weight_influence
        self.jitter_tolerance = jitter_tolerance
        self.barnes_hut_optimize = barnes_hut_optimize
        self.barnes_hut_theta = barnes_hut_theta
        self.scaling_ratio = scaling_ratio
        self.strong_gravity_mode = strong_gravity_mode
        self.gravity = gravity

        self.update()

    def _command_string(
            self, steps=100, iters_by_step=3,):
        """This will return the python code which starts the ForceAtlas2ServerCalc

        Parameters
        ----------
        steps : int, optional, default 100
        iters_by_step : int, optional, default 3

        Returns
        -------
        s : str

        """
        s = 'from helios.layouts.forceatlas2gpu import ForceAtlas2ServerCalc;'
        s += 'from fury.stream.tools import remove_shm_from_resource_tracker;'
        s += 'remove_shm_from_resource_tracker();'
        s += 'force_atlas = ForceAtlas2ServerCalc('
        s += f'edges_buffer_name="{self._shm_manager.edges._buffer_name}",'
        s += 'positions_buffer_name='
        s += f'"{self._shm_manager.positions._buffer_name}",'
        s += f'info_buffer_name="{self._shm_manager.info._buffer_name}",'
        if self._record_positions:
            s += 'snapshots_buffer_name='
            s += f'"{self._shm_manager.snapshots_positions._buffer_name}",'
        s += 'lin_log_mode ='
        s += f'{self.lin_log_mode},'
        s += 'edge_weight_influence ='
        s += f'{self.edge_weight_influence},'
        s += 'jitter_tolerance ='
        s += f'{self.jitter_tolerance},'
        s += 'barnes_hut_optimize ='
        s += f'{self.barnes_hut_optimize},'
        s += 'barnes_hut_theta ='
        s += f'{self.barnes_hut_theta},'
        s += 'scaling_ratio ='
        s += f'{self.scaling_ratio},'
        s += 'strong_gravity_mode ='
        s += f'{self.strong_gravity_mode},'
        s += 'gravity ='
        s += f'{self.gravity},'
        s += ');'
        s += f'force_atlas.start({steps},{iters_by_step});'
        return s
