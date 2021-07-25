import numpy as np
import numpy.testing as npt
from fury import window

from helios import NetworkDraw
from helios.backends.fury.actors import _MARKER2Id


def test_network_draw_only_nodes_2d_symbols(interactive=False):
    markers = list(_MARKER2Id.keys())
    num_nodes = len(markers)
    thetas = [2*np.pi*i/(num_nodes) for i in range(num_nodes)]
    positions = 2*np.array(
       [[np.cos(t), np.sin(t), 0] for t in thetas]
    )
    network_draw = NetworkDraw(
            positions=positions,
            scales=.5,
            colors=(0, 1, 0),
            node_opacity=1,
            node_edge_width=0,
            marker=markers,
    )
    if interactive:
        window.show(network_draw.showm.scene)

    arr = window.snapshot(network_draw.showm.scene)

    colors = np.array([[0, 1, 0] for i in range(num_nodes)])
    report = window.analyze_snapshot(arr, colors=colors)
    npt.assert_equal(report.objects, num_nodes)


def test_network_draw_only_nodes_3d(interactive=False):
    num_nodes = 8
    thetas = [2*np.pi*i/(num_nodes) for i in range(num_nodes)]
    positions = 2*np.array(
       [[np.cos(t), np.sin(t), 0] for t in thetas]
    )
    network_draw = NetworkDraw(
            positions=positions,
            scales=1,
            colors=(0, 1, 0),
            node_opacity=1,
            node_edge_width=0,
            marker='3d',
    )
    if interactive:
        window.show(network_draw.showm.scene)

    arr = window.snapshot(network_draw.showm.scene)

    colors = np.array([[0, 1, 0] for i in range(num_nodes)])
    report = window.analyze_snapshot(arr, colors=colors)
    npt.assert_equal(report.objects, num_nodes)


def test_network_draw_3d_update_visual_aspect(interactive=False):
    num_nodes = 8
    thetas = [2*np.pi*i/(num_nodes) for i in range(num_nodes)]
    positions = 2*np.array(
       [[np.cos(t), np.sin(t), 0] for t in thetas]
    )
    positions = np.zeros_like(positions)
    edges = np.array([[i, i+1] for i in range(num_nodes-1)])
    colors = np.random.uniform(size=(num_nodes, 3))
    edge_colors = []
    for source, target in edges:
        c0 = colors[source]
        c1 = colors[target]
        edge_colors += [c0, c1]

    edge_colors = np.array(edge_colors).astype('float64')
    for test_uniforms in [True, False]:
        test_uniforms = True
        if test_uniforms:
            node_edge_opacity = .8
            node_edge_color = [255, 255, 255]
            node_edge_width = .2
        else:
            node_edge_opacity = np.random.uniform(size=num_nodes)
            node_edge_color = np.array(colors)
            node_edge_width = np.random.uniform(size=num_nodes)/3
        node_opacity = node_edge_opacity

        network_draw = NetworkDraw(
            positions=positions,
            edges=edges,
            colors=colors,
            scales=1,
            node_edge_width=node_edge_width,
            node_edge_opacity=node_edge_opacity,
            node_opacity=node_opacity,
            node_edge_color=node_edge_color,
            marker='3d',
            edge_line_color=edge_colors,
            edge_line_opacity=.8,
            edge_line_width=1,
        )
        if not test_uniforms:
            network_draw.nodes.edge_width = np.ones(num_nodes)/2
            network_draw.nodes.edge_opacity = np.ones(num_nodes)/2
            network_draw.nodes.marker_opacity = np.random.uniform(
                size=num_nodes)
            network_draw.nodes.edge_color = np.ones((num_nodes, 3))
            network_draw.nodes.edge_color = colors - colors/2
        else:
            network_draw.nodes.edge_width = 0
            network_draw.nodes.edge_opacity = .5
            network_draw.nodes.marker_opacity = .5
            network_draw.nodes.edge_color = [1, 1, 1]

        network_draw.Render()

        if interactive:
            window.show(network_draw.showm.scene)


def test_network_draw_update_pos(interactive=False):
    num_nodes = 8
    thetas = [2*np.pi*i/(num_nodes) for i in range(num_nodes)]

    positions_2d = 2*np.array(
       [[np.cos(t), np.sin(t)] for t in thetas]
    )
    positions_3d = 2*np.array(
       [[np.cos(t), np.sin(t)] for t in thetas]
    )
    for positions in [positions_2d, positions_3d]:
        positions_0 = np.zeros_like(positions)
        network_draw = NetworkDraw(
                positions=positions,
                scales=.5,
                colors=(0, 1, 0),
                node_opacity=1,
                node_edge_width=0,
                marker='3d',
        )

        if interactive:
            window.show(network_draw.showm.scene)

        arr = window.snapshot(network_draw.showm.scene)

        colors = np.array([[0, 1, 0] for i in range(num_nodes)])
        report = window.analyze_snapshot(arr, colors=colors)
        npt.assert_equal(report.objects, num_nodes)
        network_draw.positions = positions_0
        network_draw.update()
        arr = window.snapshot(network_draw.showm.scene)
        report = window.analyze_snapshot(arr, colors=colors)
        npt.assert_equal(report.objects, 1)
