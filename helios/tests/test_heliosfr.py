import networkx as nx
import numpy as np
from fury import window

from helios import NetworkDraw
from helios.layouts import HeliosFr


def test_draw(interactive=False):
    s = 100
    sizes = [s, s, s]
    pin = .7
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

    for dimension in [2, 3]:
        centers = np.random.normal(size=(len(g), dimension))
        network_draw = NetworkDraw(
                positions=centers,
                colors=colors,
                scales=1,
                node_edge_width=0,
                node_opacity=1,
                marker='o',

        )
        layout = HeliosFr(edges_list, network_draw, update_interval_workers=10)
        layout.steps(300)
        if interactive:
            window.show(network_draw.showm.scene)
