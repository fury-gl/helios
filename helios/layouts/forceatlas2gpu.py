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
    def __init__(
        self,
        edges_buffer_name,
        positions_buffer_name,
        info_buffer_name,
        weights_buffer_name=None,
    ):
        super().__init__(
            edges_buffer_name,
            positions_buffer_name,
            info_buffer_name,
            weights_buffer_name,
            2,
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

    def start(self, steps=100, iters_by_step=3):
        for i in range(steps):
            self._pos_cudf = cg.layout.force_atlas2(
                self._G,
                max_iter=iters_by_step,
                pos_list=self._pos_cudf,
                outbound_attraction_distribution=True,
                lin_log_mode=False,
                edge_weight_influence=1.0,
                jitter_tolerance=1.0,
                barnes_hut_optimize=True,
                barnes_hut_theta=1.0,
                scaling_ratio=2.0,
                strong_gravity_mode=False,
                gravity=1.0,
                verbose=False,
                callback=None)

            self._update(
                self._pos_cudf.to_pandas().to_numpy()[:, 0:2])
        # to inform that everthing worked
        self._shm_manager.info._repr[1] = 1


class ForceAtlas2(NetworkLayoutIPCRender):
    def __init__(
        self,
        edges,
        network_draw,
        weights=None,
    ):

        super().__init__(
            network_draw,
            edges,
            weights,
        )
        if not network_draw._is_2d:
            raise ValueError('ForceAtlas2 only works for 2d layouts')

        if not CUDF_AVAILABLE:
            raise ImportError(' You need to install cugraph and cudf first')

        self.update()

    def _command_string(
            self, steps=100, iters_by_step=3,):
        s = 'from helios.layouts.forceatlas2gpu import ForceAtlas2ServerCalc;'
        s += 'from fury.stream.tools import remove_shm_from_resource_tracker;'
        s += 'remove_shm_from_resource_tracker();'
        s += 'force_atlas = ForceAtlas2ServerCalc('
        s += f'edges_buffer_name="{self._shm_manager.edges._buffer_name}",'
        s += 'positions_buffer_name='
        s += f'"{self._shm_manager.positions._buffer_name}",'
        s += f'info_buffer_name="{self._shm_manager.info._buffer_name}",'
        s += ');'
        s += f'force_atlas.start({steps},{iters_by_step});'
        return s
