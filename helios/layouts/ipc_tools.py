"""Module that provides some objects to deal with inter-process communication
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
    def __init__(
            self, dimension, dtype='float64', num_elements=None):
        """This implements a abstract (generic) ArrayBufferManager.
        The GenericArrayBufferManager is used for example to share the
        positions, edges and weights between different process.

       Parameters
        ----------
        dimension : int
        dtype : dtype
        num_elements : int, optional
                In MacOs a shared memory resource can be created with
                a different number of elements then the original data
        """
        self._dtype = dtype
        self._dimension = dimension
        self._num_elements = num_elements

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
            self,  dimension, dtype, data=None, buffer_name=None,
            num_elements=None):
        """An implementation of a GenericArrayBufferManager using SharedMemory

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
            num_elements : int, optional
                In MacOs a shared memory resource can be created with
                a different number of elements then the original data
        """
        super().__init__(dimension, dtype, num_elements)
        self._released = False
        if buffer_name is None:
            self.create_mem_resource(data)
        else:
            self.load_mem_resource(buffer_name)

    def create_mem_resource(self, data):
        self._num_elements = data.shape[0]
        self._buffer = shared_memory.SharedMemory(
                        create=True, size=data.nbytes)
        self._created = True
        self.create_repr()

        if self._repr.shape[0] >= data.shape[0]:
            self._repr[0:data.shape[0]] = data
        else:
            self._repr[:] = data

    def load_mem_resource(self, buffer_name):
        self._buffer = shared_memory.SharedMemory(buffer_name)
        self._created = False
        self.create_repr()

    def create_repr(self):
        s_bytes = np.array([1], dtype=self._dtype).nbytes
        self._num_elements_buffer = self._buffer.size//s_bytes//self._dimension
        if self._dimension == 1:
            shape = self._num_elements_buffer
        else:
            shape = (self._num_elements_buffer, self._dimension)
        self._repr = np.ndarray(
                    shape,
                    dtype=self._dtype,
                    buffer=self._buffer.buf)
        self._buffer_name = self._buffer.name

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
        return self._repr[0:self._num_elements]

    @data.setter
    def data(self, data):
        equal_dim = self._repr.shape[1] == data.shape[1]
        if self._repr.shape[0] > data.shape[0] and equal_dim:
            self._repr[0:data.shape[0]] = data.astype(self._dtype)
        elif self._repr.shape[0] == data.shape[0] and equal_dim:
            self._repr[:] = data.astype(self._dtype)


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

    def load_array(
            self, attr_name, buffer_name, dimension, dtype,
            num_elements=None):
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
            num_elements : int, optional
                In MacOs a shared memory resource can be created with
                a different number of elements then the original data

        """
        if attr_name in self._shm_attr_names:
            raise ValueError(f'A Shared Memory array with the name {attr_name}\
                is already in this ShmManager')
        _shm = SharedMemArrayManager(
            buffer_name=buffer_name, dimension=dimension, dtype=dtype,
            num_elements=num_elements)
        self._shm_attr_names.append(attr_name)
        setattr(self, attr_name, _shm)

    def cleanup(self):
        for _shm_name in self._shm_attr_names:
            getattr(self, _shm_name).cleanup()
