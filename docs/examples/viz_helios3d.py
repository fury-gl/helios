"""
=======================================
Force-Directed: SBM Model and 3d Layout
=======================================

The goal of this example is to show how to use the Helios Network
draw with the Helios Force-Directed. To run this you should
have python 3.8 or greater.

"""
import numpy as np
import networkx as nx
import argparse
from fury.window import record

from helios import NetworkDraw
from helios.layouts import HeliosFr

parser = argparse.ArgumentParser()
parser.add_argument(
    '--interactive', dest='interactive', default=True, action='store_false')
args = parser.parse_args()

interactive = args.interactive
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

centers = np.random.normal(size=(len(g), 3))

network_draw = NetworkDraw(
        positions=centers,
        edges=edges,
        colors=colors,
        scales=1,
        node_edge_width=0,
        marker=markers,
        edge_line_color=edge_colors,
        window_size=(600, 600)
)


layout = HeliosFr(
    edges, network_draw, update_interval_workers=0, max_workers=2)

###############################################################################
# The final step ! Visualize and save the result of our creation! Please,
# switch interactive variable to True if you want to visualize it.

if not interactive:
    layout.steps(100)
    record(
        network_draw.showm.scene, out_path='viz_helios2d.png', size=(600, 600))

if interactive:
    layout.start()
    network_draw.showm.initialize()
    network_draw.showm.start()

