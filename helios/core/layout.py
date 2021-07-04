from abc import ABC, ABCMeta, abstractmethod
import numpy as np

from fury.stream.tools import IntervalTimer

import heliosFR


class NetworkLayout(ABC):
    @abstractmethod
    def steps(self, iterations=1):
        ...

    @property
    def positions(self):
        return self._super_actor.positions

    @positions.setter
    def positions(self, new_positions):
        # check if it is float32 and dimensions
        self._positions = new_positions

    def update_in_vtk(self):
        self._super_actor.positions = self._positions
        self._super_actor.update()
        self.window.Render()


class NetworkLayoutAsync(NetworkLayout, metaclass=ABCMeta):
    @abstractmethod
    def start(self, max_iterations=None):
        ...

    @abstractmethod
    def stop(self):
        ...

    def __del__(self):
        self.stop()


class HeliosFr(NetworkLayoutAsync):
    def __init__(
        self,
        initial_positions,
        edges,
        network_draw,
        viscosity=0.3, a=0.0006, b=1,
        max_workers=8, update_interval_workers=0,
        velocities=None
    ):

        self._started = False
        self.window = network_draw.showm.window
        self._interval_timer = None
        self._nodes_count = initial_positions.shape[0]
        self._update_interval_workers = update_interval_workers
        self._super_actor = network_draw

        self._positions = np.ascontiguousarray(
            initial_positions, dtype=np.float32)
        self._edges = np.ascontiguousarray(edges, dtype=np.uint64)

        if velocities is None:
            velocities = np.zeros((self._nodes_count, 3), dtype=np.float32)

        self._layout = heliosFR.FRLayout(
            self._edges, self._positions, velocities, a, b, viscosity,
            maxWorkers=max_workers,
            updateInterval=self._update_interval_workers)

    def start(self, ms=15):
        if self._started:
            return

        self._layout.start()
        self._started = True

        if ms > 0:
            if ms < self._update_interval_workers:
                ms = self._update_interval_workers

            def callback():
                self.update_in_vtk()
            self._interval_timer = IntervalTimer(
                    ms/1000, callback)

    def stop(self):
        if not self._started:
            return

        if self._interval_timer is not None:
            self._interval_timer.stop()
            self._interval_timer = None
        self._layout.stop()
        self._started = False

    def steps(self, iterations=1):
        self._layout.iterate(iterations=iterations)
        self.update_in_vtk()
