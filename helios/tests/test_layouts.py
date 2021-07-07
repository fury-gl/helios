import numpy as np
import numpy.testing as npt
import pymde

from fury import window

from helios import NetworkDraw
from helios.backends.fury.actors import _MARKER2Id
from helios.layouts import MDE


def test_mde_penaltie(interactive=False):
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
        penaltie_name='logistic',
        penaltie_parameters=[.4, .5],
        constraint_name='standardized'
    )
    # before start, this element represents if
    # the MDE computations has finishded without
    # errors
    assert mde._shm_manager.info._repr[1] == 0
    mde.start(2, 10, 10)
    if interactive:
        window.show(network.showm.scene)

    while mde._started:
        ...
    assert mde._shm_manager.info._repr[1] == 1
    mde._shm_manager.cleanup()


def test_mde(interactive=False):
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
    # the MDE computations has finishded without
    # errors
    assert mde._shm_manager.info._repr[1] == 0
    mde.start(2, 10, 10)
    if interactive:
        window.show(network.showm.scene)

    while mde._started:
        ...
    assert mde._shm_manager.info._repr[1] == 1
    mde._shm_manager.cleanup()
