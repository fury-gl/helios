import pytest

import fury.shaders as fs

from helios.backends.fury.tools import Uniform, Uniforms


def test_uniform_tools():
    uniform = Uniform('uniform_name', 'f', 1.)
    assert uniform.vtk_func_uniform == 'SetUniformf'
    assert uniform.value == 1.

    class Dummy_Program:
        def SetUniformf(self, name, value):
            """camel case because we need to simulate the
            program used in vtk with the same attr name
            """
            assert name == 'uniform_name'
            assert value == 1.
            # uniform set for {name} and value {value}

    dummy_program = Dummy_Program()
    uniform.execute_program(dummy_program)

    # invalid uniform type should create an exception
    with pytest.raises(Exception):
        fs.Uniform('uniform_name', 'invalid_type', 1.)

    # creating an Uniforms object
    uniforms = Uniforms([uniform])
    # invalid uniform list  should create an exception
    with pytest.raises(Exception):
        Uniforms([1, '--'])

    # test __call__ method used in callback
    uniforms(None, None)
