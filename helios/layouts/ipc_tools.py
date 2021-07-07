"""Module that provide some objects to deal with inter-process communication"""

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
    def __init__(
            self, dimension, dtype='float64'):
        """This implements a abstract (generic) ArrayBufferManager.
        The GenericArrayBufferManager is used for example to share the
        positions, edges and weights between different process.

       Parameters
        ----------
        dimension : int
        dtype : dtype
        """
        self._dtype = dtype
        self._dimension = dimension

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
    def __init__(
            self,  dimension, dtype, data=None, buffer_name=None):
        """An implementation of GenericArrayBufferManager using SharedMemory

        Parameters:
        -----------
            dimension : int
                number of columns
            dtype : str
                type of the ndarray
            data : ndarray
                bi-dimensional array
            buffer_name : str
                buffer_name, if you pass that, then
                this Obj. will try to load the memory resource
        """
        super().__init__(dimension, dtype)
        if buffer_name is None:
            self.create_mem_resource(data)
        else:
            self.load_mem_resource(buffer_name)

    def create_mem_resource(self, data):
        self._buffer = shared_memory.SharedMemory(
                        create=True, size=data.nbytes)
        self._created = True
        self.create_repr()
        self._repr[:] = data

    def load_mem_resource(self, buffer_name):
        self._buffer = shared_memory.SharedMemory(buffer_name)
        self._created = False
        self.create_repr()

    def create_repr(self):
        s_bytes = np.array([1], dtype=self._dtype).nbytes
        self._num_nodes = self._buffer.size//s_bytes//self._dimension
        if self._dimension == 1:
            shape = self._num_nodes
        else:
            shape = (self._num_nodes, self._dimension)
        self._repr = np.ndarray(
                    shape,
                    dtype=self._dtype,
                    buffer=self._buffer.buf)
        self._buffer_name = self._buffer.name

    def cleanup(self):
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


class ShmManagerMultiArrays:
    def __init__(self):
        """This Obj. allows to deal with multiple arrays
        stored using SharedMemory
        """
        self._shm_attr_names = []

    def add_array(self, attr_name, data, dimension, dtype):
        """This creates a shared memory resource
        to store the data. The shared memory obj will be accessible
        through
        >>> self.attr_name

        Parameters:
        -----------
            attr_name: str
                used to associate a new attribute 'attr_name'
                with the current (self) ShmManagerMultiArrays.
            data : ndarray
            dimension : int
            dtype : str

        """
        if attr_name in self._shm_attr_names:
            raise ValueError(f'A Shared Memory array with the name {attr_name}\
                is already in this ShmManager')
        _shm = SharedMemArrayManager(
            data=data.astype(dtype), dimension=dimension, dtype=dtype)
        self._shm_attr_names.append(attr_name)
        setattr(self, attr_name, _shm)

    def load_array(self, attr_name, buffer_name, dimension, dtype):
        """This will load the shared memory resource associate with buffer_name
        into the current ShmManagerMultiArrays
        The shared memory obj will be accessible
        through
        >>> self.attr_name

        Parameters:
        -----------
            attr_name : str
                this name will be used to associate a new attribute 'attr_name'
                with the current (self) ShmManagerMultiArrays.
            buffer_name : str
            dimension : int
            dtype : str

        """
        if attr_name in self._shm_attr_names:
            raise ValueError(f'A Shared Memory array with the name {attr_name}\
                is already in this ShmManager')
        _shm = SharedMemArrayManager(
            buffer_name=buffer_name, dimension=dimension, dtype=dtype)
        self._shm_attr_names.append(attr_name)
        setattr(self, attr_name, _shm)

    def cleanup(self):
        for _shm_name in self._shm_attr_names:
            getattr(self, _shm_name).cleanup()
