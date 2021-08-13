
import numpy as np
from helios import NetworkDraw
from helios.backends.fury.actors import FurySuperLabels


def test_text_draw():
    interactive = False
    centers = np.array([
        [0, 0, 0],
        [1, 0, 0.],
        [0, 1., 0.]
    ])*5
    network_draw = NetworkDraw(
            positions=centers,
            scales=0.1,
            marker='3d',
    )

    def get_labels(centers):
        labels = [
            f'({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})'
            for center in centers
        ]
        return labels

    labels = get_labels(centers)
    # generate random labels
    network_labels = FurySuperLabels(
        centers,
        labels,
        min_label_size=50,
        scales=0.1
    )
    network_draw.showm.scene.add(network_labels.vtk_actor)

    dx = np.array([
        [-1, 0, 1],
        [1, 0, 1],
        [0, 1, 1]
    ])
    data = {'i': 0.}
    total = 100
    if interactive:
        def update_positions(_, __):
            new_positions = centers + dx*data['i']/total
            network_draw.positions = new_positions
            network_labels.positions = new_positions
            labels = get_labels(new_positions)
            network_labels.labels = labels
            data['i'] += 1
            network_labels.recompute_labels()
            network_draw.refresh()
        network_draw.showm.add_timer_callback(True, 10, update_positions)
        network_draw.showm.start()
    else:
        new_positions = centers + d
        network_draw.positions = new_positions
        network_labels.positions = new_positions
        labels = get_labels(new_positions)
        network_labels.labels = labels
        network_labels.recompute_labels()
        network_draw.refresh()
