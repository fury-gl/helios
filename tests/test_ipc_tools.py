import numpy as np
import numpy.testing as npt

import helios.layouts.ipc_tools as ipc


def test_shared_mem_array():
    dimension = 2
    arr = np.random.normal(size=(4, dimension))
    shm = ipc.SharedMemArrayManager(
        data=arr)
    npt.assert_equal(shm._repr, arr)

    shm_h = ipc.SharedMemArrayManager(
        buffer_name=shm._buffer_name,
        dtype=arr.dtype
    )
    shm_h._repr[0] = np.array([-1, -1]).astype(arr.dtype)
    npt.assert_equal(shm_h._repr, shm._repr)
    shm_h.cleanup()
    shm.cleanup()

    arr = np.random.normal(size=4)
    shm = ipc.SharedMemArrayManager(
        data=arr, dtype=arr.dtype)
    assert shm._repr.ndim == 1


def test_shm_manager_multi_arrays():
    shm_manager = ipc.ShmManagerMultiArrays()
    arr2d = np.random.normal(size=(4, 2))
    arr1d = np.random.normal(size=5)
    shm_manager.add_array(
        attr_name='arr2d', data=arr2d)
    shm_manager.add_array(
        attr_name='arr1d', data=arr1d)
    npt.assert_equal(shm_manager.arr2d._repr, arr2d)
    npt.assert_equal(shm_manager.arr1d._repr, arr1d)

    shm_manager_h = ipc.ShmManagerMultiArrays()
    shm_manager_h.load_array(
        attr_name='arr2d_h', buffer_name=shm_manager.arr2d._buffer_name,
        dtype=arr2d.dtype)
    shm_manager_h.load_array(
        attr_name='arr1d_h', buffer_name=shm_manager.arr1d._buffer_name,
        dtype=arr1d.dtype)
    npt.assert_equal(shm_manager_h.arr2d_h._repr, arr2d)
    npt.assert_equal(shm_manager_h.arr1d_h._repr, arr1d)
