"""VTK Super Actors

This modules contains the VTK super actors to be used in the 
network visualization.


"""

import numpy as np
from fury.shaders import add_shader_callback, attribute_to_actor
from fury.shaders import shader_to_actor, load
import fury.primitive as fp
from fury.utils import get_actor_from_primitive
from fury.utils import vertices_from_actor, array_from_actor
from fury.utils import update_actor
from fury.actor import line as line_actor
try:
    from fury.shaders import shader_apply_effects
except ImportError:
    shader_apply_effects = None

from fury import window

from helios.backends.fury.tools import Uniform, Uniforms

_MARKER2Id = {
    'o': 0, 's': 1, 'd': 2, '^': 3, 'p': 4,
    'h': 5, 's6': 6, 'x': 7, '+': 8, '3d': 0}


class FurySuperNode:
    def __init__(
        self,
        positions,
        colors=(0, 1, 0),
        scales=1,
        marker='3d',
        edge_width=.0,
        edge_opacity=1,
        edge_color=(1, 1, 1),
        marker_opacity=.8,
        write_frag_depth=True
    ):
        self._vcount = positions.shape[0]
        self._composed_by_superactors = False

        # to avoid any kind of expansive calculations when we
        # are dealing with just 2d markers
        self._marker_is_3d = marker == '3d'
        self._write_frag_depth = write_frag_depth
        self._marker_is_uniform = isinstance(marker, str)
        self._marker = marker if self._marker_is_uniform else None

        self._edge_color_is_uniform = len(edge_color) == 3
        self._edge_opacity_is_uniform = isinstance(edge_opacity, (float, int))
        self._marker_opacity_is_uniform = isinstance(
                marker_opacity, (float, int))
        self._edge_width_is_uniform = isinstance(edge_width, (float, int))
        # self._edge_color_is_uniform = len(edge_color) == 3
        self._positions_is_uniform = False
        self._init_actor(
            positions.shape[0], colors, scales)
        self.positions = positions
        self.uniforms_list = []

        self._init_marker_property(marker)
        self._init_edge_width_property(edge_width)
        self._init_edge_color_property(edge_color)
        self._init_edge_opacity_property(edge_opacity)
        self._init_marker_opacity_property(marker_opacity)
        self._init_specular_strength_property(25)
        self._init_specular_mix_property(1.)
        self._init_shadow_mix_property(0.25)

        if len(self.uniforms_list) > 0:
            self.Uniforms = Uniforms(self.uniforms_list)
            self.uniforms_observerId = add_shader_callback(
                    self.vtk_actor, self.Uniforms)

        self._init_shader_frag()

        self.blending = 'additive'
        self.depth_test = True
        self._id_observer_effects = None

    def start_effects(self, render_window):

        if self._id_observer_effects is not None:
            self.vtk_actor.GetMapper().RemoveObserver(
                self._id_observer_effects)
        effects = []
        if self.depth_test:
            effects += [window.gl_enable_depth]
        else:
            effects += [window.gl_disable_depth]

        blendings = {
            'additive': window.gl_set_additive_blending,
            'subtractive': window.gl_set_subtractive_blending,
            'multiplicative': window.gl_set_multiplicative_blending,
            'normal': window.gl_set_normal_blending,
        }
        effects += [blendings[self.blending]]
        self._id_observer_effects = shader_apply_effects(
            render_window, self.vtk_actor,
            effects=effects)

    def _init_actor(self, num_nodes, colors, scales):

        # to avoid memory corruption
        centers = np.zeros((num_nodes, 3))

        verts, faces = fp.prim_square()
        res = fp.repeat_primitive(
            verts, faces, centers=centers,
            colors=colors,
            scales=scales)

        big_verts, big_faces, big_colors, big_centers = res
        actor = get_actor_from_primitive(
            big_verts, big_faces, big_colors)
        actor.GetMapper().SetVBOShiftScaleMethod(False)
        actor.GetProperty().BackfaceCullingOff()

        attribute_to_actor(actor, big_centers, 'center')

        self._centers_geo = array_from_actor(actor, array_name="center")
        self._centers_geo_orig = np.array(self._centers_geo)
        self._centers_length = int(self._centers_geo.shape[0] / num_nodes)
        self._verts_geo = vertices_from_actor(actor)
        self._verts_geo_orig = np.array(self._verts_geo)

        self._colors_geo = array_from_actor(actor, array_name="colors")

        self.vtk_actor = actor
        # update to correct positions

    def _init_marker_property(self, data):
        if self._marker_is_uniform:
            if isinstance(data, str):
                data = _MARKER2Id[data]
            self.uniforms_list.append(
                Uniform(
                    name='marker', uniform_type='f', value=data))
        else:
            if isinstance(data[0], str):
                data = [_MARKER2Id[i] for i in data]
            data = np.repeat(data, 4).astype('float')
            attribute_to_actor(
                self.vtk_actor,
                data, 'vMarker')
            self._marker = array_from_actor(
                self.vtk_actor, array_name="vMarker")

    def _init_edge_color_property(self, edge_color):
        if self._edge_color_is_uniform:
            self.uniforms_list.append(
                Uniform(
                    name='edgeColor', uniform_type='3f', value=edge_color))
        else:
            edge_color_by_vertex = np.repeat(
                edge_color, 4, axis=0).astype('float')
            attribute_to_actor(
                self.vtk_actor,
                edge_color_by_vertex,
                'vEdgeColor')
            self._edge_color = array_from_actor(
                self.vtk_actor, array_name="vEdgeColor")

    def _init_edge_width_property(self, edge_width):
        if self._edge_width_is_uniform:
            self.uniforms_list.append(
                Uniform(
                    name='edgeWidth', uniform_type='f', value=edge_width))
        else:
            edge_width_by_vertex = np.repeat(edge_width, 4).astype('float')
            attribute_to_actor(
                self.vtk_actor,
                edge_width_by_vertex,
                'vEdgeWidth')
            self._edge_width = array_from_actor(
                self.vtk_actor, array_name="vEdgeWidth")

    def _init_edge_opacity_property(self, opacity):
        if self._edge_opacity_is_uniform:
            self.uniforms_list.append(
                Uniform(
                    name='edgeOpacity', uniform_type='f', value=opacity))
        else:
            edge_opacity_by_vertex = np.repeat(opacity, 4).astype('float')
            attribute_to_actor(
                self.vtk_actor,
                edge_opacity_by_vertex,
                'vEdgeOpacity')
            self._edge_opacity = array_from_actor(
                self.vtk_actor, array_name="vEdgeOpacity")

    def _init_marker_opacity_property(self, opacity):
        if self._marker_opacity_is_uniform:
            self.uniforms_list.append(
                Uniform(
                    name='markerOpacity', uniform_type='f', value=opacity))
        else:
            marker_opacity_by_vertex = np.repeat(opacity, 4).astype('float')
            attribute_to_actor(
                self.vtk_actor,
                marker_opacity_by_vertex,
                'vMarkerOpacity')
            self._marker_opacity = array_from_actor(
                self.vtk_actor, array_name="vMarkerOpacity")

    def _init_specular_strength_property(self, value):
        if self._marker_opacity_is_uniform:
            self.uniforms_list.append(
                Uniform(
                    name='specularStrength', uniform_type='f', value=value))

    def _init_shadow_mix_property(self, value):
        if self._marker_opacity_is_uniform:
            self.uniforms_list.append(
                Uniform(
                    name='shadowMix', uniform_type='f', value=value))

    def _init_specular_mix_property(self, value):
        if self._marker_opacity_is_uniform:
            self.uniforms_list.append(
                Uniform(
                    name='specularMix', uniform_type='f', value=value))

    @property
    def shader_dec_vert(self):
        shader = load("billboard_dec.vert")
        if not self._marker_is_3d and not self._marker_is_uniform:
            shader += """
                    in float vMarker;\n
                    out float marker;\n"""
        if not self._edge_width_is_uniform:
            shader += 'in float vEdgeWidth; \nout float edgeWidth;\n'
        if not self._edge_color_is_uniform:
            shader += 'in vec3 vEdgeColor;\n out vec3 edgeColor;\n'
        if not self._edge_opacity_is_uniform:
            shader += 'in float vEdgeOpacity;\n out float edgeOpacity;\n'
        if not self._marker_opacity_is_uniform:
            shader += 'in float vMarkerOpacity;\n out float markerOpacity;\n'

        return shader

    @property
    def shader_impl_vert(self):
        shader = load("billboard_impl.vert")
        if not self._marker_is_3d and not self._marker_is_uniform:
            shader += "marker = vMarker;\n"
        if not self._edge_width_is_uniform:
            shader += 'edgeWidth = vEdgeWidth;\n'
        if not self._edge_width_is_uniform:
            shader += 'edgeColor = vEdgeColor;\n'
        if not self._edge_opacity_is_uniform:
            shader += 'edgeOpacity = vEdgeOpacity;\n'
        if not self._edge_opacity_is_uniform:
            shader += 'markerOpacity = vMarkerOpacity;\n'

        return shader

    @property
    def shader_dec_frag(self):
        shader = load("billboard_dec.frag")
        if self._marker_opacity_is_uniform:
            shader += "uniform float markerOpacity;\n"
        else:
            shader += 'in float markerOpacity;\n'
        if self._edge_opacity_is_uniform:
            shader += "uniform float edgeOpacity;\n"
        else:
            shader += 'in float edgeOpacity;\n'
        if self._edge_width_is_uniform:
            shader += "uniform float edgeWidth;\n"
        else:
            shader += 'in float edgeWidth;\n'
        if self._edge_color_is_uniform:
            shader += "uniform vec3 edgeColor;\n"
        else:
            shader += 'in vec3 edgeColor;\n'
        if self._marker_is_uniform:
            shader += "uniform float marker;\n"
        else:
            shader += "in float marker;\n"

        shader += "uniform float specularStrength;\n"
        shader += "uniform float specularMix;\n"
        shader += "uniform float shadowMix;\n"

        shader += """
            uniform mat4 MCDCMatrix;
            uniform mat4 MCVCMatrix;

            float ndot(vec2 a, vec2 b ) {
                return a.x*b.x - a.y*b.y;
            }
            vec3 getDistFunc0(vec2 p, float s, float edgeWidth){
                //circle or sphere sdf func
                float  sdf = 0;
                float minSdf = 0;

                edgeWidth = edgeWidth/2.;
                minSdf = 0.5;
                sdf = -length(p) + s;

                vec3 result = vec3(sdf, minSdf, edgeWidth);
                return result ;
            }
            vec3 getDistFunc1(vec2 p, float s, float edgeWidth){
                //square sdf func
                edgeWidth = edgeWidth/2.;
                float minSdf = 0.5/2.0;
                vec2 d = abs(p) - vec2(s, s);
                float sdf = -length(max(d,0.0)) - min(max(d.x,d.y),0.0);

                vec3 result = vec3(sdf, minSdf, edgeWidth);
                return result ;
            }
            vec3 getDistFunc2(vec2 p, float s, float edgeWidth){
                //diamond sdf func

               edgeWidth = edgeWidth/4.;
               float minSdf = 0.5/2.0;
                vec2 b  = vec2(s, s/2.0);
                vec2 q = abs(p);
                float h = clamp((-2.0*ndot(q,b)+ndot(b,b))/dot(b,b),-1.0,1.0);
                float d = length( q - 0.5*b*vec2(1.0-h,1.0+h) );
                float sdf = -d * sign( q.x*b.y + q.y*b.x - b.x*b.y );

                vec3 result = vec3(sdf, minSdf, edgeWidth);
                return result ;
            }

            vec3 getDistFunc3(vec2 p, float s, float edgeWidth){
                float l = s/1.5;
                float minSdf = 1000.0;
                float k = sqrt(3.0);
                p.x = abs(p.x) - l;
                p.y = p.y + l/k;
                if( p.x+k*p.y>0.0 ) p = vec2(p.x-k*p.y,-k*p.x-p.y)/2.0;
                p.x -= clamp( p.x, -2.0*l, 0.0 );
                float sdf = length(p)*sign(p.y);
                vec3 result = vec3(sdf, minSdf, edgeWidth);
                return result ;
            }
            vec3 getDistFunc4(vec2 p, float s, float edgeWidth){
                edgeWidth = edgeWidth/4.;
                float minSdf = 0.5/2.0;
                float r = s/2.0;
                const vec3 k = vec3(0.809016994,0.587785252,0.726542528);
                p.x = abs(p.x);
                p -= 2.0*min(dot(vec2(-k.x,k.y),p),0.0)*vec2(-k.x,k.y);
                p -= 2.0*min(dot(vec2( k.x,k.y),p),0.0)*vec2( k.x,k.y);
                p -= vec2(clamp(p.x,-r*k.z,r*k.z),r);
                float sdf = -length(p)*sign(p.y);
                vec3 result = vec3(sdf, minSdf, edgeWidth);
                return result ;
            }
            vec3 getDistFunc5(vec2 p, float s, float edgeWidth){
                edgeWidth = edgeWidth/4.;
                float minSdf = 0.5/2.0;
                float r = s/2.0;
                const vec3 k = vec3(-0.866025404,0.5,0.577350269);
                p = abs(p);
                p -= 2.0*min(dot(k.xy,p),0.0)*k.xy;
                p -= vec2(clamp(p.x, -k.z*r, k.z*r), r);
                float sdf = -length(p)*sign(p.y);
                vec3 result = vec3(sdf, minSdf, edgeWidth);
                return result ;
            }
            vec3 getDistFunc6(vec2 p, float s, float edgeWidth){
                float minSdf = 0.5/2.0;
                edgeWidth = edgeWidth/4.;
                float r = s/2.0;
                const vec4 k = vec4(-0.5,0.8660254038,0.5773502692,1.7320508076);
                p = abs(p);
                p -= 2.0*min(dot(k.xy,p),0.0)*k.xy;
                p -= 2.0*min(dot(k.yx,p),0.0)*k.yx;
                p -= vec2(clamp(p.x,r*k.z,r*k.w),r);
                float sdf = -length(p)*sign(p.y);
                vec3 result = vec3(sdf, minSdf, edgeWidth);
                return result ;
            }
            vec3 getDistFunc7(vec2 p, float s, float edgeWidth){
                edgeWidth = edgeWidth/8.;
                float minSdf = 0.5/4.0;
                float r = s/4.0;
                float w = 0.5;
                p = abs(p);
                float sdf = -length(p-min(p.x+p.y,w)*0.5) + r;
                vec3 result = vec3(sdf, minSdf, edgeWidth);
                return result ;
            }
            vec3 getDistFunc8(vec2 p, float s, float edgeWidth){
                edgeWidth = edgeWidth/4.;
                float minSdf = 0.5/2.0;
                float r = s/15.0; //corner radius
                vec2 b = vec2(s/1.0, s/3.0); //base , size
                //vec2 b = vec2(r, r);
                p = abs(p); p = (p.y>p.x) ? p.yx : p.xy;
                vec2  q = p - b;
                float k = max(q.y,q.x);
                vec2  w = (k>0.0) ? q : vec2(b.y-p.x,-k);
                float sdf = -sign(k)*length(max(w,0.0)) - r;
                vec3 result = vec3(sdf, minSdf, edgeWidth);
                return result ;
            }

            """
        # shader += """
        #     vec3 getDistFunc(vec2 p, float s, float edgeWidth, int marker){
        #         vec3 result = vec3(0., 0., 0.);
        #         switch (marker) {
        #     """
        # for i in range(0, 9):
        #     shader += f"""
        #         case {i}:
        #             result = getDistFunc{i}(p, s, edgeWidth);
        #             break;
        #     """
        dist_func_str = """
            vec3 getDistFunc(vec2 p, float s, float edgeWidth, float marker){
                vec3 result = vec3(0., 0., 0.);
                if (marker==0.) {
                    result = getDistFunc0(p, s, edgeWidth);
            """
        for i in range(1, 9):
            dist_func_str += f"""
                {'}'}else if(marker=={i}.){'{'}
                    result = getDistFunc{i}(p, s, edgeWidth);
            """
        dist_func_str += "\n}\nreturn result;\n}\n"
        shader += dist_func_str
        return shader

    @property
    def shader_impl_frag(self):
        shader = load("billboard_impl.frag")

        shader += """

        float len = length(point);
        float radius = 1.;
        float s = 0.5;
        vec3 result = getDistFunc(point.xy, s, edgeWidth, marker);
        """
        shader += """
            float sdf = result.x;
            float minSdf = result.y;
            float edgeWidthNew = result.z;

            if (sdf<0.0) discard;"""

        if self._marker_is_3d:
            shader += """
            /* Calculating the 3D distance d from the center */
            float d = sqrt(1. - len*len);

            /* Calculating the normal as if we had a sphere of radius len*/
            vec3 normalizedPoint = normalize(vec3(point.xy, sdf));

            /* Defining a fixed light direction */
            vec3 direction = normalize(vec3(1., 1., 1.));

            /* Calculating diffuse */
            float ddf = max(0, dot(direction, normalizedPoint));

            /* Calculating specular */
            float ssf = pow(ddf, specularStrength);

            /* Calculating colors based on a fixed light */
            color = max(color*shadowMix+ddf * color, ssf * vec3(specularMix));
            """
        if self._write_frag_depth and self._marker_is_3d:
            shader += """
            /* Obtaining the two clipping planes for depth buffer */
            float far = gl_DepthRange.far;
            float near = gl_DepthRange.near;

            /* Getting camera Z vector */
            vec3 cameraZ = vec3(MCVCMatrix[0][2], MCVCMatrix[1][2], MCVCMatrix[2][2]);

            /* Get the displaced position based on camera z by adding d
            in this direction */
            vec4 positionDisplaced = vec4(centerVertexMCVSOutput.xyz
                                        +cameraZ*d,1.0);

            /* Projecting the displacement to the viewport */
            vec4 positionDisplacedDC = (MCDCMatrix*positionDisplaced);

            /* Applying perspective transformation to z */
            float depth = positionDisplacedDC.z/positionDisplacedDC.w;

            /* Interpolating the z of the displacement between far and near planes */
            depth = ((far-near) * (depth) + near + far) / 2.0;

            /* Writing the final depth to depth buffer */
            gl_FragDepth = depth;
            """
        shader += """
            vec4 rgba = vec4(  color, markerOpacity );
            if (edgeWidthNew > 0.0){
                if (sdf < edgeWidthNew) {
                    rgba = vec4(edgeColor, edgeOpacity);
                }
            }

            fragOutput0 = rgba;

        """

        return shader

    def _init_shader_frag(self):
        # fs_impl_code = load('billboard_impl.frag')
        # if self._marker_is_3d:
        #     fs_impl_code += f'{load("billboard_spheres_impl.frag")}'
        # else:
        #     fs_impl_code += f'{load("marker_billboard_impl.frag")}'
        shader_to_actor(
            self.vtk_actor,
            "vertex", impl_code=self.shader_impl_vert,
            decl_code=self.shader_dec_vert)
        shader_to_actor(
            self.vtk_actor,
            "fragment", decl_code=self.shader_dec_frag)
        shader_to_actor(
            self.vtk_actor,
            "fragment", impl_code=self.shader_impl_frag,
            block="light")

    @property
    def edge_width(self):
        if self._edge_width_is_uniform:
            return self.Uniforms.edgeWidth.value
        else:
            return self._edge_width[0::self._centers_length]

    @edge_width.setter
    def edge_width(self, data):
        if self._edge_width_is_uniform:
            self.Uniforms.edgeWidth.value = data
        else:
            self._edge_width[:] = np.repeat(
                data, self._centers_length, axis=0)
            self.update()

    @property
    def marker(self):
        if self._marker_is_uniform:
            return self.Uniforms.marker.value
        else:
            return self._marker[::self._centers_length]

    @marker.setter
    def marker(self, data):
        if self._marker_is_3d:
            raise ValueError('3d markers cannot be changed')

        if self._marker_is_uniform:
            if isinstance(data, str):
                data = _MARKER2Id[data]
            self.Uniforms.marker.value = data
        else:
            if isinstance(data[0], str):
                data = [_MARKER2Id[i] for i in data]
            self._marker[:] = np.repeat(
                data, self._centers_length, axis=0)
            self.update()

    @property
    def edge_color(self):
        if self._edge_color_is_uniform:
            return self.Uniforms.edgeColor.value
        else:
            return self._edge_color[::self._centers_length]

    @edge_color.setter
    def edge_color(self, data):
        if self._edge_color_is_uniform:
            self.Uniforms.edgeColor.value = data
        else:
            self._edge_color[:] = np.repeat(
                data, self._centers_length, axis=0)
            self.update()

    @property
    def marker_opacity(self):
        if self._marker_opacity_is_uniform:
            return self.Uniforms.markerOpacity.value
        else:
            return self._marker_opacity[::self._centers_length]

    @marker_opacity.setter
    def marker_opacity(self, data):
        if self._marker_opacity_is_uniform:
            self.Uniforms.markerOpacity.value = data
        else:
            self._marker_opacity[:] = np.repeat(
                data, self._centers_length, axis=0)
            self.update()

    @property
    def edge_opacity(self):
        if self._edge_opacity_is_uniform:
            return self.Uniforms.edgeOpacity.value
        else:
            return self._edge_opacity[::self._centers_length]

    @edge_opacity.setter
    def edge_opacity(self, data):
        if self._edge_opacity_is_uniform:
            self.Uniforms.edgeOpacity.value = data
        else:
            self._edge_opacity[:] = np.repeat(
                data, self._centers_length, axis=0)
            self.update()

    @property
    def specular_strength(self):
        return self.Uniforms.specularStrength.value

    @specular_strength.setter
    def specular_strength(self, data):
        self.Uniforms.specularStrength.value = data

    @property
    def specular_mix(self):
        return self.Uniforms.specularMix.value

    @specular_mix.setter
    def specular_mix(self, data):
        self.Uniforms.specularMix.value = data

    @property
    def shadow_mix(self):
        return self.Uniforms.shadowMix.value

    @shadow_mix.setter
    def shadow_mix(self, data):
        self.Uniforms.shadowMix.value = data

    @property
    def positions(self):
        return self._centers_geo[0::self._centers_length]

    @positions.setter
    def positions(self, positions):
        # avoids memory corruption
        self._centers_geo[:] = np.repeat(
            positions, self._centers_length, axis=0).astype('float64')
        self._verts_geo[:] = self._verts_geo_orig + self._centers_geo
        self.update()

    @property
    def colors(self):
        return self._colors_geo[0::self._centers_length]

    @colors.setter
    def colors(self, new_colors):
        self._colors_geo[:] = np.repeat(
            new_colors, self._centers_length, axis=0)

    def update(self):
        update_actor(self.vtk_actor)

    def __str__(self):
        return f'FurySuperActorNode num_nodes {self._vcount}'

    def __repr__(self):
        return f'FurySuperActorNode num_nodes {self._vcount}'


class FurySuperEdge:
    def __init__(
        self,
        edges,
        positions,
        colors,
        opacity=.5,
        line_width=3,
        blending='additive',
    ):

        self.edges = edges
        self._num_edges = len(self.edges)
        self.vtk_actor = line_actor(
            np.zeros((self._num_edges, 2, 3)),
            colors=colors,
            linewidth=line_width,
            opacity=opacity
        )

        self._is_2d = len(positions[0]) == 2
        self.positions = positions
        self._colors_geo = array_from_actor(
            self.vtk_actor, array_name="colors")

        self.blending = blending
        self.depth_test = True
        self._id_observer_effects = None

    def start_effects(self, render_window):

        if self._id_observer_effects is not None:
            self.vtk_actor.GetMapper().RemoveObserver(
                self._id_observer_effects)
        effects = [window.gl_enable_blend]
        if self.depth_test:
            effects += [window.gl_enable_depth]
        else:
            effects += [window.gl_disable_depth]

        blendings = {
            'additive': window.gl_set_additive_blending,
            'subtractive': window.gl_set_subtractive_blending,
            'multiplicative': window.gl_set_multiplicative_blending,
            'normal': window.gl_set_normal_blending,
        }
        effects += [blendings[self.blending]]
        self._id_observer_effects = shader_apply_effects(
            render_window, self.vtk_actor,
            effects=effects)

    @property
    def positions(self):
        pass

    @positions.setter
    def positions(self, positions):
        """positions never it's a uniform variable
        """
        # avoids memory corruption

        edges_positions = vertices_from_actor(self.vtk_actor)
        edges_positions[::2] = positions[self.edges[:, 0]]
        edges_positions[1::2] = positions[self.edges[:, 1]]
        update_actor(self.vtk_actor)

    @property
    def colors(self):
        return self._colors_geo

    @colors.setter
    def colors(self, new_colors):
        self._colors_geo[:] = new_colors

    def update(self):
        update_actor(self.vtk_actor)


class NetworkSuperActor():
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
        write_frag_depth=True
    ):
        self._is_2d = positions.shape[1] == 2
        if self._is_2d:
            positions = np.array([
                            positions[:, 0], positions[:, 1],
                            np.zeros(positions.shape[0])]).T

        self.nodes = FurySuperNode(
            positions=positions,
            colors=colors,
            scales=scales,
            marker=marker,
            edge_opacity=node_edge_opacity,
            edge_width=node_edge_width,
            edge_color=node_edge_color,
            marker_opacity=node_opacity,
            write_frag_depth=write_frag_depth
        )

        self.vtk_actors = [self.nodes.vtk_actor]

        if edges is not None:
            edges = FurySuperEdge(
                edges, positions, edge_line_color, opacity=edge_line_opacity,
                line_width=edge_line_width)

            self.vtk_actors += [edges.vtk_actor]

        self.edges = edges

    @property
    def positions(self):
        return self.nodes.positions

    @positions.setter
    def positions(self, positions):
        if positions.shape[1] == 2:
            positions = np.array([
                positions[:, 0], positions[:, 1],
                np.zeros(positions.shape[0])]).T
        self.nodes.positions = positions
        if self.edges is not None:
            self.edges.positions = positions

    def update(self):
        for actor in self.vtk_actors:
            update_actor(actor)

