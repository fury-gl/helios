"""
=======================================================
ForceAtlas2 using cugraph
=======================================================

The goal of this example is to show how to use the Helios Network 
draw with the ForceAtlas2 from cugraph. To run this you should 
have python 3.8 or greater and cudf/cugraph installed.

"""
import numpy as np
import networkx as nx

from helios import NetworkDraw
from helios.layouts import ForceAtlas2

size = 1000
s = size
sizes = [s, s, s]
probs = np.array(
    [[0.45, 0.05, 0.02], [0.05, 0.45, 0.07], [0.02, 0.07, 0.40]])/10
g = nx.stochastic_block_model(sizes, probs, seed=0)

num_nodes = len(g)
edges = []
for source, target in g.edges():
    edges.append([source, target])
edges = np.array(edges)

colors_by_block = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

edge_colors = []
for source, target in g.edges():
    c0 = colors_by_block[source//s]
    c1 = colors_by_block[target//s]
    edge_colors += [c0, c1]

colors_by_block = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
colors = np.array(
    [colors_by_block[i//s]
     for i in range(len(g))]).astype('float64')

markers = [['o', 's', 'd'][i//s] for i in range(len(g))]
edge_colors = np.array(edge_colors).astype('float64')

centers = np.random.normal(size=(len(g), 2))

network_draw = NetworkDraw(
        positions=centers,
        edges=edges,
        colors=colors,
        scales=1,
        node_edge_width=0,
        marker=markers,
        edge_line_color=edge_colors,
)

forceatlas2 = ForceAtlas2(
    edges, network_draw,
)

forceatlas2.start(3, 300, 1, False)
interactive = True

if interactive:
    network_draw.showm.initialize()
    network_draw.showm.start()
