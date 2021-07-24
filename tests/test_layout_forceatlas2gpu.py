import networkx as nx
import numpy as np
import time
try:
    import cudf
    import cugraph as cg
    CUDF_AVAILABLE = True
except ImportError:
    CUDF_AVAILABLE = False

from fury import window

from helios import NetworkDraw
from helios.layouts import ForceAtlas2


def test_draw(interactive=False):
    s = 10
    sizes = [s, s, s]
    pin = 1
    pout = .1
    probs = np.array([[pin, pout, pout], [pout, pin, pout], [pout, pout, pin]])
    g = nx.stochastic_block_model(sizes, probs, seed=0)
    edges_list = []
    for source, target in g.edges():
        edges_list.append([source, target])
    edges_list = np.array(edges_list)

    colors_by_block = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    colors = np.array(
        [colors_by_block[i//s]
            for i in range(len(g))]).astype('float64')

    centers = np.random.normal(size=(len(g), 2))
    network_draw = NetworkDraw(
            positions=centers,
            colors=colors,
            scales=1,
            node_edge_width=0,
            node_opacity=1,
            marker='o',

    )
    layout = ForceAtlas2(edges_list, network_draw)
    layout.start(2, 10, 10)
    if interactive:
        window.show(network_draw.showm.scene)

    time.sleep(1)
    i = 0
    while layout._started:
        i += 1
        time.sleep(1/10)
        if i > 400:
            raise TimeoutError('ForceAtlas2 timeout error')
    assert layout._shm_manager.info._repr[1] == 1
    layout._shm_manager.cleanup()
