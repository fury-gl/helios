from abc import ABC, ABCMeta, abstractmethod
import time
import sys
import subprocess
import numpy as np

from fury.stream.tools import IntervalTimer

from helios.layouts.ipc_tools import ShmManagerMultiArrays


class NetworkLayout(ABC):
    @abstractmethod
    def steps(self, iterations=1):
        ...

    @property
    def positions(self):
        return self._super_actor.positions

    @positions.setter
    def positions(self, new_positions):
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


def is_running(p, timeout=0):
    '''Check if a given process is running

    Parameters:
    ----------
        p : process
        timeout : float, optional
            positive float
    Returns:
    --------
        running : bool
    '''
    try:
        p.wait(timeout=timeout)
        running = False
    except subprocess.TimeoutExpired:
        assert p.returncode is None
        running = True
    return running


class NetworkLayoutIPCServerCalc(ABC):
    def __init__(
        self,
        edges_buffer_name,
        positions_buffer_name,
        info_buffer_name,
        weights_buffer_name=None,
        dimension=3,
    ):
        """An abstract class which reads the network information
        from the shared memory resources. Usually, this should be used
        inside of a subprocess which will update the network layout positions

        Parameters:
        ----------
            edges_buffer_name : str
            positions_buffer_name : str
            info_buffer_name : str
            weights_buffer_name : str, optional
            dimension : int

        """
        self._dimension = dimension

        self._shm_manager = ShmManagerMultiArrays()
        self._shm_manager.load_array(
            'info', buffer_name=info_buffer_name, dimension=1,
            dtype='float32')
        self._shm_manager.load_array(
            'positions', buffer_name=positions_buffer_name,
            dimension=self._dimension,
            dtype='float32')

        self._shm_manager.load_array(
            'edges', buffer_name=edges_buffer_name, dimension=2, dtype='int64')

        if weights_buffer_name is not None:
            self._shm_manager.load_array(
                'weights', buffer_name=edges_buffer_name,
                dimension=1, dtype='float32')

    @abstractmethod
    def start(self, steps=100, iters_by_step=3):
        """This method starts the network layout algorithm.
        Parameters:
        -----------
            steps : int
            iters_by_step: int
        """
        ...

    def _update(self, positions):
        """This method update the shared memory resource
        which stores the network positions. Usualy, you
        should call this in the start method implementation

        Parameters:
        -----------
            positions : ndarray

        """
        self._shm_manager.positions._repr[:] = positions.astype('float32')
        self._shm_manager.info._repr[0] = time.time()

    def __del__(self):
        self._shm_manager.cleanup()


class NetworkLayoutIPCRender(ABC):
    def __init__(self, network_draw, edges, weights=None):
        """An abstract class which reads the network information
        and creates the shared memory resources.

        Parameters:
        -----------
            network_draw : NetworkDraw
            edges : ndarray
                a bi-dimensional array with the edges list
            weights : array

        """
        self._started = False
        self._interval_timer = None
        self._pserver = None
        self._network_draw = network_draw
        self._dimension = 2 if network_draw._is_2d else 3
        self._shm_manager = ShmManagerMultiArrays()
        self._shm_manager.add_array(
            'positions',
            network_draw.positions[:, 0:self._dimension],
            self._dimension,
            'float32'
        )
        self._shm_manager.add_array(
            'info',
            np.array([0, 0]),
            1,
            'float32'
        )
        self._shm_manager.add_array(
            'edges',
            edges,
            2,
            'int64'
        )
        if weights is not None:
            self._shm_manager.add_array(
                'weights',
                weights,
                1,
                'float32'
            )

    @abstractmethod
    def _command_string(self, steps, iters_by_step):
        """Used inside of the start method.

        Parameters:
        -----------
            steps : int
                number of steps; snapshots.
                For example, if you set steps=3 that means the positions will
                be updated three times.
            iters_by_step : int

        Returns:
        --------
            command_string : str
                a string with a code that starts the layout algorithm.
        """
        ...

    def _update(self):
        self._network_draw.positions = self._shm_manager.positions._repr.\
            astype('float64')
        self._network_draw.Render()

    def start(self, ms=30, steps=100, iters_by_step=2):
        """This method starts the network layout algorithm creating a
        new subprocess. Right after the network layout algorithm
        finish the computation (ending of the related subprocess),
        the stop method will be called automatically.

        Parameters
        -----------
            ms : float
                time interval in milleseconds to update the positions inside
                of the NetworkDraw
            steps : int
                number of steps; snapshots.
                For example, if you set steps=3 that means the positions will
                be updated three times.
            iters_by_step : int
                number of interations in each step

        """
        if self._started:
            return
        self._last_update = time.time()
        args = [
            sys.executable, '-c',
            self._command_string(steps, iters_by_step)
        ]
        self._pserver = subprocess.Popen(
            args,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        if ms > 0:

            def callback():
                last_update = self._shm_manager.info._repr[0]
                # if stop has been called inside the treading timer
                # maybe another callback can be executed
                if self._pserver is None:
                    return
                # if the process finished then stop the callback
                if not is_running(self._pserver, 0):
                    self.stop()
                self._last_update = last_update
                self._update()

            self._interval_timer = IntervalTimer(
                    ms/1000, callback)
        self._started = True

    def stop(self):
        """Stop the layout algorithm
        """
        if not self._started:
            return

        if self._interval_timer is not None:
            self._interval_timer.stop()
            self._interval_timer = None

        if self._pserver is not None:
            self._pserver.kill()
            self._pserver.wait()
            self._pserver = None

        self._started = False

    def cleanup(self):
        self._shm_manager.cleanup()

    def __del__(self):
        self.stop()
        self.cleanup()
