# Helios Networks [WIP]

This package will cover complex network representations, layouts and
visualizations.

<h1 align="center">
  <br>
  <a href="https://www.heliosnetwork.io"><img src="https://heliosnetwork.io/_images/logo.png" alt="helios" width="200"></a>
  <br>Helios Network and Streaming Visualization Lib<br>

</h1>

<p>
Helios is a Python library that aims to provide an easy way to
visualize huge networks dynamically. Helios also provides visualizations through 
an interactive stadia-like streaming system in which users can be 
collaboratively access (and share) visualizations created in a server or through Jupyter Notebook/Lab environments.'
</p>




<p align="center">
  <a href="#general-information">General Information</a> •
  <a href="#key-features">Key Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#how-to-use">How to use</a> •
  <a href="#credits">Credits</a> •
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

**Step 1.** Get the latest source by cloning this repo:

    git clone https://github.com/fury-gl/helios.git

**Step 2.** Install requirements:

    pip install -r requirements.txt

**Step 3.** Install Helios

As a [local project installation](https://pip.pypa.io/en/stable/reference/pip_install/#id44) using:

    pip install .

Or as an ["editable" installation](https://pip.pypa.io/en/stable/reference/pip_install/#id44) using:

    pip install -e .


**Step 4:** Enjoy!

For more information, see also [installation page on heliosnetwork.io](https://heliosnetwork.io/latest/installation.html)

## Testing

After installation, you can install test suite requirements:

    pip install -r requirements_dev.txt

And to launch test suite:

    pytest -svv helios


# How to use

There are many ways to start using FURY:

- Go to [Getting Started](https://heliosnetwork.io/getting_started.html)
- Explore our [Examples](https://heliosnetwork.io/examples_gallery/index.html) or [API](https://heliosnetwork.io/latest/auto_examples/index.htmlhttps://heliosnetwork.io/api.html).


# Credits

Please, go to [contributors
page](https://github.com/fury-gl/helios/graphs/contributors) to see who have been
involved in the development of Helios.
