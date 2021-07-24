"""VTK/FURY Tools

This module implements a set o tools to enhance VTK given new functionalities.

"""


class Uniform:
    """This creates a uniform shader variable

    It's responsible to store the value of a given uniform
    variable and call the related vtk_program

    """
    def __init__(self, name, uniform_type, value):
        """

        Parameters
        ----------
        name: str
            name of the uniform variable
        uniform_type: str
            Uniform variable type which will be used inside the shader.
            Any of this are valid: 1fv, 1iv, 2f, 2fv, 2i, 3f, 3fv,
                3uc, 4f, 4fv, 4uc, GroupUpdateTime, Matrix,
                Matrix3x3, Matrix4x4, Matrix4x4v, f, i
                value: float or ndarray
        value: type(uniform_type)
            should be a value which represent's the shader uniform
            variable. For example, if uniform_type is 'f' then value
            should be a float; if uniform_type is '3f' then value
            should be a 1x3 array.

        """
        self.name = name
        self.value = value
        self.uniform_type = uniform_type

        self.valid_types = [
            '1fv', '1iv', '2f', '2fv', '2i', '3f', '3fv',
            '3uc', '4f', '4fv', '4uc', 'GroupUpdateTime', 'Matrix',
            'Matrix3x3', 'Matrix4x4', 'Matrix4x4v', 'f', 'i']
        if self.uniform_type not in self.valid_types:
            raise ValueError(
                f"""Uniform type {self.uniform_type} not valid.
                Choose one of this values: {self.valid_types}""")

        self.vtk_func_uniform = f'SetUniform{self.uniform_type}'

    def execute_program(self, program):
        """ Given a shader program, this method
        will update the value with the associated uniform variable
        in a draw call

        Parameters
        ----------
        program: vtkmodules.vtkRenderingOpenGL2.vtkShaderProgram
            A shader program which will be used to update the uniform

        """
        program.__getattribute__(self.vtk_func_uniform)(
                self.name, self.value)

    def __repr__(self):
        return f'Uniform(name={self.name}, value={self.value})'


class Uniforms:
    def __init__(self, uniforms):
        """Creates an object which store and execute an uniform variable.

        Parameters
        -----------
        uniforms: list
            List of Uniform objects.

        Examples
        --------

        .. highlight:: python
        .. code-block:: python

            uniforms = [
                Uniform(name='edgeWidth', uniform_type='f', value=edgeWidth)...
            ]
            CustomUniforms = Uniforms(markerUniforms)
            add_shader_callback(
                    sq_actor, CustomUniforms)
            sq_actor.CustomUniforms = CustomUniforms
            sq_actor.CustomUniforms.edgeWidth = 0.5

        """
        self.uniforms = uniforms
        for obj in self.uniforms:
            # if isinstance(obj, Uniform) is False:
            #    raise ValueError(f"""{obj} it's not an Uniform object""")

            setattr(self, obj.name, obj)

    def __call__(self, _caller, _event, calldata=None,):
        """This method should be used as a callback for a vtk Observer

        Execute the shader program with the given uniform variables.

        """
        program = calldata
        if program is None:
            return None

        for uniform in self.uniforms:
            uniform.execute_program(program)

    def __repr__(self):
        return f'Uniforms({[obj.name for obj in self.uniforms]})'
