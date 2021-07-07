import torch
import pymde

from helios.layouts.base import NetworkLayoutIPCRender
from helios.layouts.base import NetworkLayoutIPCServerCalc


class MDEServerCalc(NetworkLayoutIPCServerCalc):
    def __init__(
        self,
        edges_buffer_name,
        positions_buffer_name,
        info_buffer_name,
        weights_buffer_name=None,
        dimension=3,
        distortion_function=None,
        use_shortest_path=False
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
        elif distortion_function is None:
            distortion = pymde.penalties.Quadratic(weights_torch)
        else:
            distortion = distortion_function(weights_torch)
        self.mde = pymde.MDE(
           self._shm_manager.positions._repr.shape[0],
           self._dimension,
           edges_torch,
           distortion,
           # constraint=pymde.Standardized()
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


class MDE(NetworkLayoutIPCRender):
    def __init__(
        self,
        edges,
        network_draw,
        weights=None,
        use_shortest_path=True,
    ):

        super().__init__(
            network_draw,
            edges,
            weights,
        )
        self._use_shortest_path = use_shortest_path
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
        s += f'dimension={self._dimension});'
        s += f'mde_h.start({steps},{iters_by_step});'
        s += 'mde_h.cleanup();'

        return s
