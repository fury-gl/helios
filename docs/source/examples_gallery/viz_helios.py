"""
=======================================================
Visualize Interdisciplinary map of the journals network
=======================================================

The goal of this app is to show an overview of the journals network structure
as a complex network. Each journal is shown as a node and their connections
indicates a citation between two of them.

"""

###############################################################################
# First, let's import some useful functions

from os.path import join as pjoin
from fury import colormap as cmap
from fury.window import record
import numpy as np

###############################################################################
# Then let's download some available datasets.

from fury.data.fetcher import fetch_viz_wiki_nw

from helios import NetworkDraw
from helios.layouts.force_directed import HeliosFr

files, folder = fetch_viz_wiki_nw()
categories_file, edges_file, positions_file = sorted(files.keys())

###############################################################################
# We read our datasets

positions = np.loadtxt(pjoin(folder, positions_file))
positions = np.random.normal(scale=10, size=positions.shape)
categories = np.loadtxt(pjoin(folder, categories_file), dtype=str)
edges = np.loadtxt(pjoin(folder, edges_file), dtype=int)

###############################################################################
# We attribute a color to each category of our dataset which correspond to our
# nodes colors.

category2index = {category: i
                  for i, category in enumerate(np.unique(categories))}


index2category = np.unique(categories)

categoryColors = cmap.distinguishable_colormap(nb_colors=len(index2category))

colors = np.array([categoryColors[category2index[category]]
                   for category in categories])

###############################################################################
# We define our node size

radii = 1 + np.random.rand(len(positions))

###############################################################################
# Lets create our edges now. They will indicate a citation between two nodes.
# OF course, the colors of each edges will be an interpolation between the two
# node that it connects.

#edgesPositions = []
edgesColors = []
for source, target in edges:
    #edgesPositions.append(np.array([positions[source], positions[target]]))
    edgesColors.append(np.array([colors[source], colors[target]]))

#edgesPositions = np.array(edgesPositions)
edgesColors = np.average(np.array(edgesColors), axis=1)

###############################################################################
# Our data preparation is ready, it is time to visualize them all. We start to
# build 2 actors that we represent our data : sphere_actor for the nodes and
# lines_actor for the edges.


network_draw = NetworkDraw(
        positions=positions,
        colors=colors,
        scales=4,
        node_edge_width=0,
        edge_line_color=edgesColors,
        marker='3d',
        edges=edges,
)
layout = HeliosFr(edges, network_draw, update_interval_workers=10)

layout.start()
###############################################################################
# The final step ! Visualize and save the result of our creation! Please,
# switch interactive variable to True if you want to visualize it.

interactive = False 
if not interactive:
    import time
    time.sleep(10)
    layout.stop()

if interactive:
    network_draw.showm.initialize()
    network_draw.showm.start()

record(
    network_draw.showm.scene, out_path='viz_helios.png', size=(600, 600))
