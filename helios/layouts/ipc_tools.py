"""Inter-Process communication tools

This Module provides abstract classes and objects to deal with inter-process
communication.

References
----------
    [1]“Python GSoC - Post #3: Network layout algorithms using IPC -
    demvessias’s Blog.”
    `blogs.python-gsoc.org/en/demvessiass-blog/post-3
    <https://blogs.python-gsoc.org/en/demvessiass-blog/post-3-network-layout-algorithms-using-ipc/>`_ 
    (accessed Jul. 24, 2021).

"""

import numpy as np
from abc import ABC, abstractmethod

import sys
if sys.version_info.minor >= 8:
    from multiprocessing import shared_memory
    PY_VERSION_8 = True
else:
    shared_memory = None
    PY_VERSION_8 = False


class GenericArrayBufferManager(ABC):
    """This implements a abstract (generic) ArrayBufferManager.

    The GenericArrayBufferManager is used for example to share the
    positions, edges and weights between different process.

    """
    def __init__(
            self,  dtype=None, data=None):
        """

        Parameters
        ----------
        dtype : dtype, optional
            The data type of the array.
        data : ndarray, optional
            The data of the array.

        """
        if data is not None:
            self._dtype = data.dtype if dtype is None else dtype
            self._data = data.astype(self._dtype)
        else:
            if dtype is None:
                raise ValueError('A dtype or data must be provided')
            self._dtype = dtype

    @abstractmethod
    def load_mem_resource(self):
        pass

    @abstractmethod
    def create_mem_resource(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass


class SharedMemArrayManager(GenericArrayBufferManager):
    """An implementation of a GenericArrayBufferManager using SharedMemory

    """
    def __init__(
            self, dtype=None, data=None, buffer_name=None):
        """

        Parameters
        ----------
        dtype : str, optional
            type of the ndarray
        data : ndarray, optional
            bi-dimensional array
        buffer_name : str
            buffer_name, if you pass that, then
            this Obj. will try to load the memory resource

        """
        super().__init__(dtype, data)
        self._released = False
        if buffer_name is None:
            self.create_mem_resource(data)
        else:
            self.load_mem_resource(buffer_name)

    def create_mem_resource(self, data):
        self._num_rows = data.shape[0]
        self._dimension = data.shape[1] if data.ndim == 2 else 1
        self._num_elements = self._num_rows*self._dimension
        buffer_arr = np.zeros(
            self._num_elements+2, dtype=data.dtype)
        self._buffer = shared_memory.SharedMemory(
                        create=True, size=buffer_arr.nbytes)

        s_bytes = np.array([1], dtype=self._dtype).nbytes
        sizes = np.ndarray(
            2, dtype=self._dtype,
            buffer=self._buffer.buf[0:s_bytes*2])
        sizes[0] = self._num_rows
        sizes[1] = self._dimension

        if self._dimension == 1:
            shape = self._num_rows
        else:
            shape = (self._num_rows, self._dimension)

        start = int(s_bytes*2)
        end = int((self._num_elements+2)*s_bytes)
        self._repr = np.ndarray(
            shape,
            dtype=self._dtype,
            buffer=self._buffer.buf[start:end])

        self._buffer_name = self._buffer.name
        self._created = True
        self._repr[:] = data

    def load_mem_resource(self, buffer_name):
        self._buffer = shared_memory.SharedMemory(buffer_name)
        s_bytes = np.array([1], dtype=self._dtype).nbytes
        sizes = np.ndarray(
            2, dtype=self._dtype,
            buffer=self._buffer.buf[0:s_bytes*2])
        self._num_rows = int(sizes[0])
        self._dimension = int(sizes[1])
        self._num_elements = self._num_rows*self._dimension
        if self._dimension == 1:
            shape = self._num_rows
        else:
            shape = (self._num_rows, self._dimension)
        start = s_bytes*2
        end = (self._num_elements+2)*s_bytes
        self._repr = np.ndarray(
            shape,
            dtype=self._dtype,
            buffer=self._buffer.buf[start:end])
        self._created = False

    def cleanup(self):
        if self._released:
            return

        self._buffer.close()
        # this it's due the python core issues
        # https://bugs.python.org/issue38119
        # https://bugs.python.org/issue39959
        # https://github.com/luizalabs/shared-memory-dict/issues/13
        if self._created:
            try:
                self._buffer.unlink()
            except FileNotFoundError:
                print(f'Shared Memory {self._buffer_name}\
                        File not found')
        self._released = True

    @property
    def data(self):
        return self._repr

    @data.setter
    def data(self, data):
        equal_dim = self._repr.shape[1] == data.shape[1]
        if self._repr.shape[0] > data.shape[0] and equal_dim:
            self._repr[0:data.shape[0]] = data.astype(self._dtype)
        elif self._repr.shape[0] == data.shape[0] and equal_dim:
            self._repr[:] = data.astype(self._dtype)

    def update_snapshot(self, data, step):
        size = data.shape[0]
        start = step*size
        end = step*size + size
        self._repr[start:end] = data.astype(self._dtype)

    def get_snapshot(self, step, size):
        start = step*size
        end = (step*size + size)
        return self._repr[start:end]


class ShmManagerMultiArrays:
    """This Obj. allows to deal with multiple arrays
        stored using SharedMemory
    """
    def __init__(self):
        self._shm_attr_names = []

    def add_array(self, attr_name, data, dtype=None):
        """This creates a shared memory resource
        to store the data.

        The shared memory obj will be accessible
        through

        >>> self.attr_name

        Parameters
        ----------
        attr_name: str
            used to associate a new attribute 'attr_name'
            with the current (self) ShmManagerMultiArrays.
        data : ndarray
        dtype : str, optional
            type of the ndarray

        """
        if attr_name in self._shm_attr_names:
            raise ValueError(f'A Shared Memory array with the name {attr_name}\
                is already in this ShmManager')
        _shm = SharedMemArrayManager(
            data=data, dtype=dtype)
        self._shm_attr_names.append(attr_name)
        setattr(self, attr_name, _shm)

    def load_array(
            self, attr_name, buffer_name, dtype):
        """This will load the shared memory resource associate with buffer_name
        into the current ShmManagerMultiArrays
        The shared memory obj will be accessible
        through

        >>> self.attr_name

        Parameters
        ----------
        attr_name : str
            this name will be used to associate a new attribute 'attr_name'
            with the current (self) ShmManagerMultiArrays.
        buffer_name : str
        dtype : str

        """
        if attr_name in self._shm_attr_names:
            raise ValueError(f'A Shared Memory array with the name {attr_name}\
                is already in this ShmManager')
        _shm = SharedMemArrayManager(
            buffer_name=buffer_name,
            dtype=dtype)
        self._shm_attr_names.append(attr_name)
        setattr(self, attr_name, _shm)

    def cleanup_mem(self, resource_name):
        if resource_name in self._shm_attr_names:
            getattr(self, resource_name).cleanup()
            self._shm_attr_names.remove(resource_name)
            delattr(self, resource_name)
        else:
            raise ValueError(f'{resource_name} is not in this ShmManager')

    def cleanup(self):
        for _shm_name in self._shm_attr_names:
            getattr(self, _shm_name).cleanup()
