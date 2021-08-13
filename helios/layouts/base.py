"""Network Layout Abstract Classes

This module provides a set of abstract classes to deal with
different network layouts algorithms using different communication
strategies.

"""

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

    def update(self):
        self._network_draw.positions = self._positions
        self._network_draw.refresh()


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
    '''Check if the process *p* is running

    Parameters
    ----------
    p : process
    timeout : float, optional
        positive float

    Returns
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
    """An abstract class which reads the network information
    from the shared memory resources.

    This should be used
    inside of a subprocess which will update the network layout positions

    """

    def __init__(
        self,
        edges_buffer_name,
        positions_buffer_name,
        info_buffer_name,
        weights_buffer_name=None,
        snaphosts_buffer_name=None,
    ):
        """

        Parameters
        ----------
        edges_buffer_name : str
        positions_buffer_name : str
        info_buffer_name : str
        weights_buffer_name : str, optional
        snaphosts_buffer_name : str, optional

        """

        self._shm_manager = ShmManagerMultiArrays()
        self._shm_manager.load_array(
            'info', buffer_name=info_buffer_name,
            dtype='float32')
        self._shm_manager.load_array(
            'positions', buffer_name=positions_buffer_name,
            dtype='float32')
        self._dimension = self._shm_manager.positions._dimension

        self._shm_manager.load_array(
            'edges', buffer_name=edges_buffer_name,
            dtype='int64')

        if weights_buffer_name is not None:
            self._shm_manager.load_array(
                'weights', buffer_name=weights_buffer_name,
                dtype='float32')

        self._record_positions = snaphosts_buffer_name is not None
        if self._record_positions:
            self._shm_manager.load_array(
                'snapshots_positions', buffer_name=snaphosts_buffer_name,
                dtype='float32')
            self._num_snapshots = self._shm_manager.snapshots_positions.\
                _num_rows

    @abstractmethod
    def start(self, steps=100, iters_by_step=3):
        """This method starts the network layout algorithm.

        Parameters
        ----------
        steps : int
            number of iterations to perform
        iters_by_step: int
            number of iterations to perform between each step

        """
        ...

    def _update(self, positions, step):
        """This method update the shared memory resource which stores the
        network positions. Usually, you should call this inside of the
        start method implementation

        Parameters
        ----------
        positions : ndarray
            a numpy array with shape (num_nodes, self._dimension)

        """
        # self._shm_manager.update_array(if self._record_positions:
        if self._record_positions:
            self._shm_manager.snapshots_positions.update_snapshot(
                positions, step % self._num_snapshots)
        self._shm_manager.positions.data = positions
        self._shm_manager.info._repr[0] = time.time()
        self._shm_manager.info._repr[2] = step

    def __del__(self):
        self._shm_manager.cleanup()


class NetworkLayoutIPCRender(ABC):
    """An abstract class which reads the network information
        and creates the shared memory resources.

    """
    def __init__(self, network_draw, edges, weights=None):
        """

        Parameters
        ----------
        network_draw : NetworkDraw
            A NetworkDraw object which will be used to draw the network
        edges : ndarray
            a bi-dimensional array with the edges list
        weights : array, optional
            a one-dimensional array with the edge weights

        """
        self._started = False
        self._interval_timer = None
        self._id_observer = None
        self._id_timer = None
        self._pserver = None
        self._network_draw = network_draw
        self._record_positions = False
        self._dimension = 2 if network_draw._is_2d else 3
        self._shm_manager = ShmManagerMultiArrays()
        self._shm_manager.add_array(
            'positions',
            network_draw.positions[:, 0:self._dimension],
            'float32'
        )
        self._shm_manager.add_array(
            'info',
            np.array([0, 0, 0]).astype('float32'),
        )
        self._shm_manager.add_array(
            'edges',
            edges,
            'int64'
        )
        if weights is not None:
            self._shm_manager.add_array(
                'weights',
                weights,
                'float32'
            )
        self._num_nodes = network_draw.positions.shape[0]
        self._num_edges = edges.shape[0]

    @abstractmethod
    def _command_string(self, steps, iters_by_step):
        """Return the python code which will compute
        the layout positions.

        Parameters
        ----------
        steps : int
            number of steps; snapshots.
            For example, if you set steps=3 that means the positions will
            be updated three times.
        iters_by_step : int

        Returns
        --------
        command_string : str
            a string with a code that starts the layout algorithm.

        """
        ...

    def update(self):
        """This method updates the position of the network actor
        and right after that refresh the network draw

        """
        if self._record_positions:
            self._network_draw.positions = self._shm_manager.\
                snapshots_positions.get_snapshot(
                    self._current_step, self._num_nodes)
            self._current_step += 1
            self._current_step = self._current_step % self._steps
        else:
            self._network_draw.positions = self._shm_manager.positions.data
        self._network_draw.refresh()

    def start(
            self, ms=30, steps=100, iters_by_step=2,
            record_positions=False, without_iren_start=True):
        """This method starts the network layout algorithm
        creating a new subprocess.

        Right after the network layout algorithm
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
        record_positions : bool, optional, default True
            Record the positions of the network
        without_iren_start : bool, optional, default True
            Set this to False if you will start the ShowManager.
            That is, if you will invoke the following commands

        Examples
        --------

            >>> network_draw.initialize()
            >>> network_draw.start()

        """
        if self._started:
            return

        self._record_positions = record_positions
        if self._record_positions:
            self._shm_manager.add_array(
                'snapshots_positions',
                np.zeros(
                    (
                        self._shm_manager.positions._num_rows*steps,
                        self._shm_manager.positions._dimension
                    )
                ).astype('float32'),
            )
            self._steps = steps
            self._current_step = 0

        self._last_update = time.time()
        args = [
            sys.executable, '-c',
            self._command_string(steps, iters_by_step)
        ]
        self._pserver = subprocess.Popen(
            args,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        if ms > 0:
            def callback_update_pos(caller, event):
                should_update = self._check_and_sync()
                if should_update:
                    self.update()

            if not without_iren_start:
                self._id_observer = \
                    self._network_draw.iren.AddObserver(
                        "TimerEvent", callback_update_pos)
                self._id_timer = \
                    self._network_draw.iren.CreateRepeatingTimer(ms)
            else:
                self._interval_timer = IntervalTimer(
                        ms/1000, callback_update_pos, *[None, None])
        self._started = True

    def _check_and_sync(self):
        """

        This will check  two conditions:
        1 - If the positions in the shared memory resources have
        changed.
        2 - If the process responsible to compute the layout positions
        finished the computations

        Returns
        -------
        should_update : bool

        """
        last_update = self._shm_manager.info._repr[0]
        self._last_update = last_update

        # if stop has been called inside the treading timer
        # maybe another callback can be executed
        ok = True
        if self._pserver is None:
            ok = False

        elif self._record_positions:
            ok = self._current_step < self._shm_manager.info._repr[2]
        # if the process finished then stop the callback
        elif not is_running(self._pserver, 0):
            self.stop()
            ok = False
        else:
            ok = True

        return ok

    def stop(self):
        """Stop the layout algorithm

        """
        if not self._started:
            return

        if self._interval_timer is not None:
            self._interval_timer.stop()
            self._interval_timer = None

        if self._id_timer is not None:
            self._network_draw.iren.DestroyTimer(self._id_timer)
            self._id_timer = None

        if self._id_observer is not None:
            self._network_draw.iren.RemoveObserver(self._id_observer)
            self._id_observer = None

        if self._pserver is not None:
            self._pserver.kill()
            self._pserver.wait()
            self._pserver = None
        if self._record_positions:
            self._shm_manager.cleanup_mem('snapshots_positions')

        self._started = False

    def cleanup(self):
        """Release the shared memory resources

        """
        self._shm_manager.cleanup()

    def __del__(self):
        self.stop()
        self.cleanup()
