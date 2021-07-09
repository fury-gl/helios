import numpy as np
import time
import pymde

from fury import window

from helios import NetworkDraw
from helios.layouts import MDE


def test_penalty(interactive=False):
    n_items = 20
    edges = pymde.all_edges(n_items).cpu().numpy()
    np.delete(edges, [1, 3, 5, 7])
    centers = np.random.normal(size=(n_items, 2))

    network = NetworkDraw(
        positions=centers,
        edges=edges
    )
    mde = MDE(
        edges, network,
        use_shortest_path=False,
        penalty_name='logistic',
        penalty_parameters=[.4, .5],
        constraint_name='standardized'
    )
    # before start, this element represents if
    # the MDE computations has finished without
    # errors
    assert mde._shm_manager.info._repr[1] == 0
    mde.start(2, 10, 10)
    if interactive:
        window.show(network.showm.scene)

    time.sleep(1)
    i = 0
    while mde._started:
        i += 1
        time.sleep(1/10)
        if i > 100:
            raise TimeoutError('MDE timeout error')
    assert mde._shm_manager.info._repr[1] == 1
    mde._shm_manager.cleanup()


def test_draw(interactive=False):
    n_items = 20
    edges = pymde.all_edges(n_items).cpu().numpy()
    np.delete(edges, [1, 3, 5, 7, 18])
    centers = np.random.normal(size=(n_items, 2))

    network = NetworkDraw(
        positions=centers,
        edges=edges
    )
    mde = MDE(
        edges, network,
        use_shortest_path=True,
        constraint_name='standardized'
    )
    # before start, this element represents if
    # the MDE computations has finished without
    # errors
    assert mde._shm_manager.info._repr[1] == 0
    mde.start(2, 10, 10)
    if interactive:
        window.show(network.showm.scene)

    time.sleep(1)
    i = 0
    while mde._started:
        i += 1
        time.sleep(1/10)
        if i > 100:
            raise TimeoutError('MDE timeout error')
    assert mde._shm_manager.info._repr[1] == 1
    mde._shm_manager.cleanup()
