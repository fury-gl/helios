"""FURY NetworkDraw

"""
from fury import window

from helios.backends.fury.actors import NetworkSuperActor


class NetworkDraw(NetworkSuperActor):
    """This object is responsible to deal with the drawing of the network.

    Attributes
    ----------
        showm : ShowManager
            A ShowManager instance from FURY
            `fury.gl/fury.window.html#showmanager <https://fury.gl/latest/reference/fury.window.html#showmanager>`_

    """
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
        """

        Parameters
        ----------
        positions : ndarray
            Array of the nodes positions.
        edges : ndarray, optional
            Array of the edges.
        colors : tuple or ndarray, optional
            Tuple of the colors of the nodes.
        scales : float or ndarray, optional
            Scaling factor for the node.
        marker : str or list, optional
            Marker for the nodes.
        node_edge_width : float or array, optional
            Width of the edges around the nodes.
        node_opacity : float or array, optional
            Opacity of the nodes.
        node_edge_opacity : float or array, optional
            Opacity of the edges.
        node_edge_color : tuple or ndarray, optional
            Color of the edges around the nodes.
        edge_line_color : tuple or ndarray, optional
            Color of the edges.
        edge_line_opacity : float or ndarray, optional
            Opacity of the edges.
        edge_line_width : float or ndarray, optional
            Width of the edges.
        better_performance : bool, optional
            Improves the performance of the draw function.
        write_frag_depth : bool, optional
            Writes in the depth buffer.
        window_size : tuple, optional
            Size of the window.
        showm : ShowManager, optional
            Fury ShowManager instance.
            `fury.gl/fury.window.html#showmanager <https://fury.gl/latest/reference/fury.window.html#showmanager>`_

        """
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
        self.iren = showm.iren
        self.window = showm.window
        self.Render = self.showm.window.Render
        self.start = self.showm.start
        self.initialize = self.showm.initialize

    def refresh(self):
        """This will refresh the FURY window instance.

        Call this method every time that you change any property in the
        network like positions, colors etc

        """
        ...
        self.window.Render()
        self.iren.Render()
