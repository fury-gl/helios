import numpy as np
import heliosFR

from fury.stream.tools import IntervalTimer
from helios.layouts.base import NetworkLayoutAsync


class HeliosFr(NetworkLayoutAsync):
    def __init__(
        self,
        edges,
        network_draw,
        viscosity=0.3, a=0.0006, b=1,
        max_workers=8, update_interval_workers=0,
        velocities=None
    ):
        """Force-directed layout method. Can be used for both 2d and
        3d layouts.

        Parameters:
        ----------
            edges : ndarray
            network_draw : NetworkDraw
            viscosity : float, optional
            a : float, optional
            b : float, optional
            max_workers : int, optional
                number of threads
            update_interval_workers : float, optional
                When you set this to a value greater than zero the
                helios-fr will wait to perform each step. This can be used
                to reduce the CPU consumption

        """

        self._started = False
        self._network_draw = network_draw
        self._interval_timer = None
        self._nodes_count = network_draw.positions.shape[0]
        self._update_interval_workers = update_interval_workers

        self._positions = np.ascontiguousarray(
            network_draw.positions, dtype=np.float32)
        self._edges = np.ascontiguousarray(edges, dtype=np.uint64)

        if velocities is None:
            velocities = np.zeros((self._nodes_count, 3), dtype=np.float32)

        self._layout = heliosFR.FRLayout(
            self._edges, self._positions, velocities, a, b, viscosity,
            maxWorkers=max_workers,
            updateInterval=self._update_interval_workers)

    def start(self, ms=15):
        """Starts the helios force-directed layout using others threads (async).

        Parameters:
        -----------
            ms : float, optional
                Interval in milleseconds to update the node
                and edge positions in the network visualization.

        """
        if self._started:
            return

        self._layout.start()
        self._started = True

        if ms > 0:
            if ms < self._update_interval_workers:
                ms = self._update_interval_workers

            self._interval_timer = IntervalTimer(
                     ms/1000, self.update)

    def stop(self):
        """This will stop the threads running the
        helios force-directed algorithm

        """
        if not self._started:
            return

        if self._interval_timer is not None:
            self._interval_timer.stop()
            self._interval_timer = None

        self._layout.stop()
        self._started = False

    def steps(self, iterations=1):
        self._layout.iterate(iterations=iterations)
        self.update()
