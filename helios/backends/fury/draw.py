from fury import window

from helios.backends.fury.actors import NetworkSuperActor


class NetworkDraw(NetworkSuperActor):
    def __init__(
        self,
        positions,
        edges=None,
        colors=(0, 1, 0),
        scales=1,
        marker='o',
        node_edge_width=.0,
        node_opacity=.8,
        node_edge_opacity=1,
        node_edge_color=(255, 255, 255),
        edge_line_color=(1, 1, 1),
        edge_line_opacity=.5,
        edge_line_width=1,
        better_performance=False,
        write_frag_depth=True,
        window_size=(400, 400),
        showm=None,
        **kwargs

    ):
        if better_performance:
            write_frag_depth = False

        super().__init__(
            positions,
            edges,
            colors,
            scales,
            marker,
            node_edge_width,
            node_opacity,
            node_edge_opacity,
            node_edge_color,
            edge_line_color,
            edge_line_opacity,
            edge_line_width,
            write_frag_depth
        )

        self.scene = window.Scene()
        for actor in self.vtk_actors:
            self.scene.add(actor)

        if self._is_2d:
            interactor_style = 'image'
            self.scene.SetBackground((255, 255, 255))
        else:
            interactor_style = 'custom'
        if showm is None:
            showm = window.ShowManager(
                self.scene,
                size=window_size,
                interactor_style=interactor_style,
                **kwargs
            )
        self.showm = showm
        self.Render = self.showm.window.Render
