============
Installation
============

Helios supports Python 3.7+. 

Dependencies
------------

The mandatory dependencies are:

- numpy >= 1.7.1
- vtk >= 8.1.0
- fury

The optional dependencies are:

- opencv
- cugraph


Installation with PyPi
----------------------

In a terminal, issue the following command

.. code-block:: shell

    pip install helios



Installation via Source
-----------------------

**Step 1.** Get the latest source by cloning this repo

.. code-block:: shell

    git clone https://github.com/fury-gl/helios.git

**Step 2.** Install requirements

.. code-block:: shell

    pip install -r requirements.txt

**Step 3.** Install helios via

.. code-block:: shell

    pip install -e .

**Step 4:** Enjoy!


Running the Tests
-----------------

Let's install all required packages for the running the test

.. code-block:: shell

    pip install -r requirements.txt
    pip install -r requirements_dev.txt

There are two ways to run Helios tests:

- From the command line. You need to be on the Helios package folder

.. code-block:: shell

    pytest -svv helios

- To run a specific test file

.. code-block:: shell

    pytest -svv helios/tests/test_actor.py

- To run a specific test directory

.. code-block:: shell

    pytest -svv helios/tests

- To run a specific test function

.. code-block:: shell

    pytest -svv -k "test_my_function_name"

Running the Tests Offscreen
---------------------------

Helios is based on VTK which uses OpenGL for all its rendering. For a headless rendering, we recommend to install and use Xvfb software on linux or OSX.
Since Xvfb will require an X server (we also recommend to install XQuartz package on OSX). After Xvfb is installed you have 2 options to run Helios tests:

- First option

.. code-block:: shell

    export DISPLAY=:0
    Xvfb :0 -screen 1920x1080x24 > /dev/null 2>1 &
    pytest -svv fury

- Second option

.. code-block:: shell

    export DISPLAY=:0
    xvfb-run --server-args="-screen 0 1920x1080x24" pytest -svv fury


Populating our Documentation
----------------------------



In our ``docs`` folder structure above:

- ``source`` is the folder that contains all ``*.rst`` files.
- ``tutorials`` is the directory where we have all python scripts that describe how to use the api.
- ``examples`` being the Helios app showcases.


Building the documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Step 1.** Install all required packages for the documentation generation

.. code-block:: shell

    pip install -U -r requirements.txt
    pip install -U -r requirements_docs_sys.txt

**Step 2.** Go to the ``docs`` folder and run the following command to generate it (Linux and macOS)

.. code-block:: shell

    make -C . clean && make -C . html

To generate the documentation without running the examples

.. code-block:: shell

    make -C . clean && make -C . html-no-examples

or under Windows

.. code-block:: shell

    make clean
    make html

To generate the documentation without running the examples under Windows

.. code-block:: shell

    make clean
    make html-no-examples


**Step 3.** Congratulations! the ``build`` folder has been generated! Go to ``build/html`` and open with browser ``index.html`` to see your generated documentation.