from helios.fury.tools import Uniform, Uniforms
from fury.shaders import add_shader_callback, attribute_to_actor
from fury.shaders import shader_to_actor, load
import fury.primitive as fp
from fury.utils import get_actor_from_primitive
from fury.utils import (vertices_from_actor, array_from_actor,
    update_actor, compute_bounds)

import numpy as np
from vtk.util import numpy_support



class FurySuperNode:
    def __init__(
        self,
        positions,
        colors=(0, 1, 0),
        scales=1,
        marker='3d',
        edge_width=.0,
        edge_color=(255, 255, 255),
    ):
        self._vcount = positions.shape[0]
        self._composed_by_superactors = False

        # to avoid any kind of expansive calculations when we
        # are dealing with just 2d markers
        self._marker_is_3d = marker == '3d'

        self._marker_is_uniform = isinstance(marker, str)
        self._edge_width_is_uniform = True 
        self._edge_color_is_uniform = True 
        self._edge_opacity_is_uniform = True 
        self._marker_opacity_is_uniform = True 
        # self._edge_width_is_uniform = isinstance(edge_width, float)
        # self._edge_color_is_uniform = len(edge_color) == 3
        self._positions_is_uniform = False

        self.vtk_actor = self._init_actor(
            positions, colors, scales)

        self.uniforms_list = []

        self._init_marker_property(marker)
        self._init_edge_width_property(edge_width)
        self._init_edge_color_property(edge_color)
        self._init_edge_opacity_property(1)
        self._init_marker_opacity_property(1)

        self.uniforms_list.append(
           Uniform(
                name='edgeOpacity', uniform_type='f', value=1))
        self.uniforms_list.append(
           Uniform(
                name='markerOpacity', uniform_type='f', value=1))

        if len(self.uniforms_list) > 0:
            self.Uniforms = Uniforms(self.uniforms_list)
            self.uniforms_observerId = add_shader_callback(
                    self.vtk_actor, self.Uniforms)

        # def callback(
        #     _caller, _event, calldata=None,
        #         uniform_type='f', uniform_name=None, value=None):
        #     program = calldata
        #     if program is not None:
        #         program.__getattribute__(f'SetUniform{uniform_type}')(
        #             uniform_name, value)

        #     from functools import partial
        #     sq_actor = self.vtk_actor
        #     add_shader_callback(
        #             sq_actor, partial(
        #                 callback, uniform_type='f', uniform_name='edgeWidth',
        #                 value=edge_width))
        #     add_shader_callback(
        #             sq_actor, partial(
        #                 callback, uniform_type='f', uniform_name='markerOpacity',
        #                 value=0))
        #     add_shader_callback(
        #             sq_actor, partial(
        #                 callback, uniform_type='f', uniform_name='edgeOpacity',
        #                 value=0))
        #     add_shader_callback(
        #             sq_actor, partial(
        #                 callback, uniform_type='3f', uniform_name='edgeColor',
        #                 value=edge_color))
            self._init_shader_frag()

    def update(self):
        update_actor(self.vtk_actor)
        compute_bounds(self.vtk_actor)

    def _init_actor(self, centers, colors, scales):
        verts, faces = fp.prim_square()
        res = fp.repeat_primitive(
            verts, faces, centers=centers,
            colors=colors,
            scales=scales)

        big_verts, big_faces, big_colors, big_centers = res
        sq_actor = get_actor_from_primitive(
            big_verts, big_faces, big_colors)
        sq_actor.GetMapper().SetVBOShiftScaleMethod(False)
        sq_actor.GetProperty().BackfaceCullingOff()

        attribute_to_actor(sq_actor, big_centers, 'center')
        return sq_actor

    def _init_marker_property(self, marker):
        marker2id = {
            'o': 0, 's': 1, 'd': 2, '^': 3, 'p': 4,
            'h': 5, 's6': 6, 'x': 7, '+': 8}

        if self._marker_is_3d:
            self._marker_is_uniform = True
        else:
            self._marker_is_uniform = False
            if isinstance(marker, str):
                list_of_markers = np.ones(self._vcount)*marker2id[marker]
            else:
                list_of_markers = [marker2id[i] for i in marker]

            list_of_markers = np.repeat(list_of_markers, 4).astype('float')
            attribute_to_actor(
                self.vtk_actor,
                list_of_markers, 'marker')

    def _init_edge_color_property(self, edge_color):
        # if self._edge_color_is_uniform:
        self.uniforms_list.append(
            Uniform(
                name='edgeColor', uniform_type='3f', value=edge_color))
        # else:
        #     edge_colors = np.repeat(
        #        edge_color, 4).astype('float')
        #     attribute_to_actor(
        #         self.vtk_actor,
        #         edge_colors, 'edgeColor')

    def _init_edge_width_property(self, edge_width):
        self.uniforms_list.append(
            Uniform(
                name='edgeWidth', uniform_type='f', value=edge_width))

    def _init_edge_opacity_property(self, opacity):
        self.uniforms_list.append(
            Uniform(
                name='edgeOpacity', uniform_type='f', value=opacity))

    def _init_marker_opacity_property(self, opacity):
        self.uniforms_list.append(
            Uniform(
                name='markerOpacity', uniform_type='f', value=opacity))

    @property
    def shader_dec_vert(self):
        shader = load("billboard_dec.vert")
        if not self._marker_is_3d:
            shader += f'\n{load("marker_billboard_dec.vert")}'
        return shader

    @property
    def shader_impl_vert(self):
        shader = load("billboard_impl.vert")
        if not self._marker_is_3d:
            shader += f'\n{load("marker_billboard_impl.vert")}'

        return shader

    @property
    def shader_dec_frag(self):
        shader = load("billboard_impl.vert")
        if not self._marker_is_3d:
            shader += f'\n{load("marker_billboard_impl.vert")}'

        return shader

    @property
    def shader_impl_frag(self):
        shader = load("billboard_impl.vert")
        if not self._marker_is_3d:
            shader += f'\n{load("marker_billboard_impl.vert")}'

        return shader

    def _init_shader_frag(self):

        fs_dec_code = load('billboard_dec.frag')
        fs_dec_code += f'\n{load("marker_billboard_dec.frag")}'
        fs_impl_code = load('billboard_impl.frag')
        if self._marker_is_3d:
            fs_impl_code += f'{load("billboard_spheres_impl.frag")}'
        else:
            fs_impl_code += f'{load("marker_billboard_impl.frag")}'

        shader_to_actor(
            self.vtk_actor,
            "vertex", impl_code=self.shader_impl_vert,
            decl_code=self.shader_dec_vert)
        shader_to_actor(
            self.vtk_actor,
            "fragment", decl_code=fs_dec_code)
        shader_to_actor(
            self.vtk_actor,
            "fragment", impl_code=fs_impl_code,
            block="light")

    @property
    def edge_width(self):
        if self._edge_width_is_uniform:
            return self.Uniforms.edgeWidth

    @edge_width.setter
    def edge_width(self, data):
        if self._edge_width_is_uniform:
            self.Uniforms.edgeWidth = data

    @property
    def marker(self):
        pass

    @marker.setter
    def marker(self, data):
        pass

    @property
    def edge_color(self):
        pass

    @edge_color.setter
    def edge_color(self, data):
        pass
    
    @property
    def positions(self):
        pass

    @positions.setter
    def positions(self, pos):
        """positions never it's a uniform variable
        """
        # spheres_positions = numpy_support.vtk_to_numpy(
        #     self.vtk_actor.GetMapper().GetInput().GetPoints().GetData())
        # spheres_positions[:] = self.sphere_geometry + \
        #     np.repeat(pos, self.geometry_length, axis=0)

        # self.vtk_actor.GetMapper().GetInput().GetPoints().GetData().Modified()
        # self.vtk_actor.GetMapper().GetInput().ComputeBounds()
        # pass

    def __str__(self):
        return f'FurySuperActorNode num_nodes {self._vcount}'

    def __repr__(self):
        return f'FurySuperActorNode num_nodes {self._vcount}'


class FurySuperActorNetwork:
    def __init__(
        self,
        positions,
        colors=(0, 1, 0),
        scales=1,
        marker='o',
        edge_width=.0,
        edge_color=(255, 255, 255),
    ):
        self._composed_by_superactors = True
        self.nodes = FurySuperNode(
            positions=positions,
            colors=colors,
            scales=scales,
            marker=marker,
            edge_width=edge_width,
            edge_color=edge_color
        )
        # self.edges = FurySuperEdges(positions, ...)

        self.vtk_actors = [self.nodes.vtk_actor, ]

    @property
    def positions(self):
        return self.nodes.positions

    @positions.setter
    def positions(self, data):
        self.nodes.positions = data
        # self.edges.positions = data
