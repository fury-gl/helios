"""
==============
Network Labels
==============

The goal of this example is to show how to use the Helios Network
draw with the Helios Force-Directed.

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

size = 100
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




def get_labels(centers):
    labels = [
        f'({center[0]:.2f}, {center[1]:.2f})'
        for center in centers
    ]
    return labels


labels = get_labels(centers)

network_draw.add_labels(
    labels, align='center', colors=(0, 0, 1),
    scales=.1,
    y_offset_ratio=5,
    min_label_size=50)

layout = HeliosFr(
    edges, network_draw, update_interval_workers=100, max_workers=2)


if interactive:
    def update_positions(_, __):
        labels = get_labels(network_draw.positions)
        network_draw.labels.labels = labels
        network_draw.labels.positions = network_draw.positions
        network_draw.refresh() 
    network_draw.showm.add_timer_callback(True, 10, update_positions)

if not interactive:
    layout.steps(100)
    record(
        network_draw.showm.scene, out_path='viz_labels.png', size=(600, 600))

if interactive:
    layout.start()
    #layout.steps(100)
    network_draw.showm.initialize()
    network_draw.showm.start()



  