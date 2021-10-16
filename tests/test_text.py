
import numpy as np
from helios import NetworkDraw


def test_text_draw():
    interactive = False
    centers = np.random.normal(0, 0.1, size=(100, 3))

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

    network_draw.add_labels(labels, min_label_size=50, scales=.1)
    network_labels = network_draw.labels
    dx = np.array([
        [-1, 0, 1],
        [1, 0, 1],
        [0, 1, 1]
    ])
    dx = 5
    data = {'i': 0.}
    total = 10
    if interactive:
        def update_positions(_, __):
            # new_positions = centers + dx*data['i']/total
            new_positions = centers + centers*data['i']/total
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
        new_positions = centers + dx
        network_draw.positions = new_positions
        network_labels.positions = new_positions
        labels = get_labels(new_positions)
        network_labels.labels = labels
        network_labels.recompute_labels()
        network_draw.refresh()
