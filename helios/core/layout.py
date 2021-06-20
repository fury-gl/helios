from abc import ABC, ABCMeta, abstractmethod
import numpy as np

from fury.stream.tools import IntervalTimer

import heliosFR


class NetworkLayout(ABC):
    def __init__(self, network, *args, positions=None, **kargs):
        self.network = network
        if(positions is not None):
            self.positions = positions
        else:
            self._positions = np.zeros((
                self.network.vertex_count(),
                self.dimensions), dtype=np.float32)

    @abstractmethod
    def steps(self, iterations=1):
        ...
   
    @property
    def positions(self):
        return self._positions

    @positions.setter
    def positions(self, new_positions):
        # check if it is float32 and dimensions
        self._positions = new_positions

    @property
    def dimensions(self):
        return 3


class NetworkLayoutAsync(NetworkLayout, metaclass=ABCMeta):
    @abstractmethod
    def start(self, max_iterations=None):
        ...
   
    @abstractmethod
    def stop(self):
        ...

    @abstractmethod
    def wait(self):
        ...

    def steps(self, iterations=1):
        self.start(max_iterations=iterations)
        self.wait()


class HeliosFr:
    def __init__(
        self,
        initial_positions,
        edges,
        showm, super_actor, viscosity=0.3, a=0.0006, b=1,
        max_workers=4, update_interval_workers=50,
        velocities=None
    ):
        self.nodes_count = initial_positions.shape[0]

        self.positions = np.ascontiguousarray(
            initial_positions, dtype=np.float32)

        self.edges = np.ascontiguousarray(edges, dtype=np.uint64)
        self.super_actor = super_actor
        self.showm = showm
        if velocities is None:
            velocities = np.zeros((self.nodes_count, 3), dtype=np.float32)

        self.layout = heliosFR.FRLayout(
            self.edges, self.positions, velocities, a, b, viscosity,
            maxWorkers=max_workers, updateInterval=update_interval_workers)
        self.update_interval_workers = update_interval_workers
        self._interval_timer = None
        self._started = False

    def start(self, ms=15):
        if self._started:
            return

        self.layout.start()
        self._started = True

        if ms > 0:
            if ms < self.update_interval_workers:
                ms = self.update_interval_workers

            def callback():
                self.update_in_vtk()
            self._interval_timer = IntervalTimer(
                    ms/1000, callback)

    def update_in_vtk(self):
        self.super_actor.positions = self.positions
        self.super_actor.update()
        self.showm.window.Render()

    def stop(self):
        if not self._started:
            return

        if self._interval_timer is not None:
            self._interval_timer.stop()
            self._interval_timer = None
        self.layout.stop()
        self._started = False

    def __del__(self):
        self.stop()
