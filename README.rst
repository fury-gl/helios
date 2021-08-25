Helios Networks
=====================
.. raw:: html
    
    <img src="https://heliosnetwork.io/_images/logo.png" width="400px">

Helios is a Python library aiming to provide an easy way to visualize huge networks dynamically. Helios also provides visualizations through an interactive Stadia-like streaming system in which users can be collaboratively access (and share) visualizations created in a server or through Jupyter Notebook/Lab environments. It incorporates state-of-the-art layout algorithms and optimized rendering techniques (powered by FURY_).


Main Goals
~~~~~~~~~~~
* Provide an advanced and optimized rendering pipeline to visualize large networks in 2D and 3D
* Make it customizable, so it can be easily adapted to user-specific needs
* Allow the to plug and unplug layout algorithms
* Provide a collaborative Web and Jupyter interface to share and explore networks in real time
* Allow the network structure to change
* Provide a basic user interface to control the view perspective and interact with the network
* Easy way to conenct network node positions, colors, and other visual features

Check out https://heliosnetwork.io/ for Documentation and Examples.


Installation
~~~~~~~~~~~
Use pip to install the latest release of helios::

    pip install helios

or get it from the source by using::

    pip git+https://github.com/fury-gl/helios.git

Helios requires Python 3.7+ and requires the following mandatory dependencies:

- numpy >= 1.7.1
- vtk >= 8.1.0
- fury

To enable WebRTC streaming and enable optimizations to the streaming system, install the following optional packages:

* Requirements for WebRTC streaming

  * aiohttp 
  * aiortc

* Optional packages that may improve performance

  * cython
  * opencv

Example usage
~~~~~~~~~~~
.. code-block:: python
   
   from helios import NetworkDraw
   from helios.layouts import HeliosFr
   import numpy as np
   
   vertex_count = 8
   
   edges = np.array([
      [0,1],
      [0,2],
      [1,2],
      [2,3],
      [3,4],
      [3,5],
      [4,5],
      [5,6],
      [6,7],
      [7,0]
   ]);
   
  centers = np.random.normal(size=(vertex_count, 3))

  network_draw = NetworkDraw(
          positions=centers,
          edges=edges,
          colors=(0.25,0.25,0.25),
          scales=1,
          node_edge_width=0,
          marker='s',
          edge_line_color=(0.5,0.5,0.5),
          window_size=(600, 600)
  )
  
  layout = HeliosFr(edges, network_draw)
  layout.start()
  network_draw.showm.initialize()
  network_draw.showm.start()
  

History
~~~~~~~~~~~
Helios project started as a replacement for the desktop version of the `Networks 3D`_ tools. The project evolved quickly over the summer 2021 due to the GSoC’21 under the responsibilities of Python Software Foundation and the FURY team. The majority of the initial work is being done by `@devmessias`_ mentored by `@filipinascimento`_ and `@skoudoro`_. The GSoC’21 project associated to Helios is “A system for collaborative visualization of large network layouts using FURY”. Check out the `final report`_ for more information.

.. _FURY: https://github.com/fury-gl/
.. _Networks 3D: https://filipinascimento.github.io/networks3d/
.. _@devmessias: https://github.com/devmessias
.. _@filipinascimento: https://github.com/filipinascimento
.. _@skoudoro: https://github.com/skoudoro
.. _`final report`: https://gist.github.com/devmessias/1cb802efb0a094686c129259498710b3 


