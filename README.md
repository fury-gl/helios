# Helios Networks [WIP]


<h1 align="center">
  <a href="https://www.heliosnetwork.io"><img src="https://heliosnetwork.io/_images/logo.png" alt="helios" width="200" style="background-color:white; padding:20px; border-radius:10px"></a>

</h1>

Helios is a Python library aiming to provide an easy way to visualize huge networks dynamically. Helios also provides visualizations through an interactive Stadia-like streaming system in which users can be collaboratively access (and share) visualizations created in a server or through Jupyter Notebook/Lab environments. It incorporates state-of-the-art layout algorithms and optimized rendering techniques (powered by [FURY](https://github.com/fury-gl/)).




<p align="center">
  <a href="#general-information">General Information</a> •
  <a href="#key-features">Key Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#how-to-use">Usage</a> •
  <a href="#history">History</a> •
  <a href="#credits">Credits</a> 
</p>


# General Information

- **Website and Documentation:**  https://heliosnetwork.io/
- **Examples:** https://heliosnetwork.io/examples_gallery/index.html
- **Blog:**  https://heliosnetwork.io/blog.html
- **Free software:** MIT license
- **Community:** Come to chat on [Discord](https://discord.gg/6btFPPj)

# Key Features

- Force-directed layout using octrees
- Minimum-distortion embeddings
- ForceAtlas2 using cugraph
- Interactive local and Remote rendering in Jupyter Notebooks
- WebRTC or MJPEG interactive streaming system


# Installation

Use pip install pointed to this repository:

    pip git+https://github.com/fury-gl/helios.git


As an alternative, Helios can be installed from the source code through the following steps:

- **Step 1.** Get the latest source by cloning this repo:

      git clone https://github.com/fury-gl/helios.git

- **Step 2.** Install requirements:

      pip install -r requirements.txt

- **Step 3.** Install Helios

    As a [local project installation](https://pip.pypa.io/en/stable/reference/pip_install/#id44) using:

        pip install .

    Or as an ["editable" installation](https://pip.pypa.io/en/stable/reference/pip_install/#id44) using:

        pip install -e .

- **Step 4:** Enjoy!

For more information, see also [installation page on heliosnetwork.io](https://heliosnetwork.io/latest/installation.html)

## Dependencies
Helios requires Python 3.7+ and the following mandatory dependencies:

- numpy >= 1.7.1
- vtk >= 8.1.0
- fury

To enable WebRTC streaming and enable optimizations to the streaming system, install the following optional packages:

* Required for WebRTC streaming

  * aiohttp 
  * aiortc

* Optional packages that may improve performance

  * cython
  * opencv


## Testing

After installation, you can install test suite requirements:

    pip install -r requirements_dev.txt

And to launch test suite:

    pytest -svv helios


# Usage

There are many ways to start using Helios:

- Go to [Getting Started](https://heliosnetwork.io/getting_started.html)
- Explore our [Examples](https://heliosnetwork.io/examples_gallery/index.html) or [API](https://heliosnetwork.io/latest/auto_examples/index.htmlhttps://heliosnetwork.io/api.html).

Example usage:
```python
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
```


# History

Helios project started as a replacement to the desktop version of the [Networks 3D](https://filipinascimento.github.io/networks3d/) tools. The project evolved quickly along the summer of 2021 due to the GSoC’21 under the responsibility of the Python Software Foundation and the FURY team. The majority of the initial work has been done by [@devmessias](https://github.com/devmessias) mentored by [@filipinascimento](https://github.com/filipinascimento) and [@skoudoro](https://github.com/skoudoro). The GSoC’21 project associated with Helios is “A system for collaborative visualization of large network layouts using FURY”. Check out the [final report](https://gist.github.com/devmessias/1cb802efb0a094686c129259498710b3) for more information.


# Credits

Please, go to [contributors
page](https://github.com/fury-gl/helios/graphs/contributors) to see who has been
involved in the development of Helios.
