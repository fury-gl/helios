#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

import os
import re
import sys
from datetime import datetime
import helios 

# Add current path
sys.path.insert(0, os.path.abspath('.'))
# Add doc in path for finding tutorial and examples
sys.path.insert(0, os.path.abspath('../..'))
# Add custom extensions
sys.path.insert(0, os.path.abspath('./ext'))

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#


# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinxext.opengraph',
    # 'IPython.sphinxext.ipython_directive',
    # 'IPython.sphinxext.ipython_console_highlighting',
    'matplotlib.sphinxext.plot_directive',
    'sphinx_copybutton',
    'ablog',
]
ogp_site_url = "http://heliosnetwork.io/"
ogp_image = "https://heliosnetwork.io/_images/logo.png"
ogp_description_length = 300

description = 'Helios is a Python library that aims to provide an easy way to \
visualize huge networks dynamically. Helios also provides visualizations through \
an interactive stadia-like streaming system in which users can be \
collaboratively access (and share) visualizations created in a server or through \
Jupyter Notebook/Lab environments.'

rst_epilog = f"""
.. |Description| replace:: {description}
"""

# ogp_custom_meta_tags = [
#     f'<meta name="description" content="{description}">',
#     '<meta name="image" content="https://heliosnetwork.io/_images/helios-og-face.png">',
#     '<meta name="twitter:card" content="summary">',
#     f'<meta name="twitter:description" content="{description}">',
#     '<meta name="og:type" content="website">'
# ]
# if 'IN_READTHEDOCS' not in os.environ.keys():
extensions.append('sphinx_gallery.gen_gallery')
# -- Options for sphinx gallery -------------------------------------------

from scrap import ImageFileScraper


class ArgvExamples:
    def __repr__(self):
        return 'ArgvExamples'

    def __call__(self, sphinx_gallery_conf, script_vars):
        return ['--interactive', ]


sc = ImageFileScraper()

sphinx_gallery_conf = {
    'doc_module': ('helios', 'helios.layouts', 'helios.backends.fury'),
    # path to your examples scripts
    'examples_dirs': ['../examples'],
    # path where to save gallery generated examples
    'gallery_dirs': ['examples_gallery'],

    'image_scrapers': (sc),
    'backreferences_dir': 'api_gallery',
    'reset_argv': ArgvExamples(),
    'reference_url': {'helios': None, },
    'filename_pattern': re.escape(os.sep)
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    'numpy': ('http://docs.scipy.org/doc/numpy/', None),
    "fury": ("https://fury.gl/latest/", None),
}

autosummary_generate = 'IN_READTHEDOCS' not in os.environ.keys()  # Turn on sphinx.ext.autosummary
# autosummary_generate = False  # Turn on sphinx.ext.autosummary
autoclass_content = "both"  # Add __init__ doc (ie. params) to class summaries
html_show_sourcelink = False  # Remove 'view source code' from top of page (for html, not python)
autodoc_inherit_docstrings = True  # If no docstring, inherit from base class
set_type_checking_flag = True  # Enable 'expensive' imports for sphinx_autodoc_typehints
autodoc_typehints = "description" # Sphinx-native method. Not as good as sphinx_autodoc_typehints

# Add any paths that contain templates here, relative to this directory.
templates_path = ['templates']


# Exclusions
# To exclude a module, use autodoc_mock_imports. Note this may increase build time, a lot.
# (Also, when installing on readthedocs.org, we omit installing Tensorflow and
# Tensorflow Probability so mock them here instead.)
#autodoc_mock_imports = [
    # 'tensorflow',
    # 'tensorflow_probability',
#]
# To exclude a class, function, method or attribute, use autodoc-skip-member. (Note this can also
# be used in reverse, ie. to re-include a particular member that has been excluded.)
# 'Private' and 'special' members (_ and __) are excluded using the Jinja2 templates; from the main
# doc by the absence of specific autoclass directives (ie. :private-members:), and from summary
# tables by explicit 'if-not' statements. Re-inclusion is effective for the main doc though not for
# the summary tables.
# def autodoc_skip_member_callback(app, what, name, obj, skip, options):
#     # This would exclude the Matern12 class and to_default_float function:
#     exclusions = ('Matern12', 'to_default_float')
#     # This would re-include __call__ methods in main doc, previously excluded by templates:
#     inclusions = ('__call__')
#     if name in exclusions:
#         return True
#     elif name in inclusions:
#         return False
#     else:
#         return skip
# def setup(app):
#     # Entry point to autodoc-skip-member
#     app.connect("autodoc-skip-member", autodoc_skip_member_callback)


napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True


# Configuration options for plot_directive. See:
# https://github.com/matplotlib/matplotlib/blob/f3ed922d935751e08494e5fb5311d3050a3b637b/lib/matplotlib/sphinxext/plot_directive.py#L81
plot_html_show_source_link = False
plot_html_show_formats = False

# Generate the API documentation when building

numpydoc_show_class_members = False

# Add any paths that contain templates here, relative to this directory.
# import ablog
# templates_path = ['_templates', ablog.get_html_templates_path(), ]


# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'Helios'
copyright = '2021-{0}, Helios'.format(datetime.now().year)
author = 'Helios'
html_logo = "imgs/logo_100.png"
html_favicon = "imgs/logo_36.ico"
# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = helios.__version__
# The full version, including alpha/beta/rc tags.
release = helios.__release__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


html_theme = 'sphinx_rtd_theme'
# html_theme_path = [sphinx_rtd_theme.get_html_theme_path(), ]

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['static']

html_style = 'css/main.css'

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    '**': [
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
        'versions.html',
    ]
}
# html_sidebars = {
#     "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"],
# }
# html_sidebars = {
#     "introduction/**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"],
#     "getting_started": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"],
#     "auto_examples/**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"],
#     "auto_tutorials/**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"],
#     "references/**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"],
#     "blog": ["categories.html", "archives.html"],
#     "blog/**": ["categories.html", "archives.html"],
#     "posts/**": ["postcard.html"],
# }


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'helios'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'helios.tex', 'FURY Documentation',
     'Contributors', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'helios', 'Helios Documentation',
     [author], 1)
]



# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'helios', 'Helios Documentation',
     author, 'helios', 'Helios Network Visualization',
     'Miscellaneous'),
]

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/reference/', None),
    'matplotlib': ('https://matplotlib.org', None),
}
autodoc_mock_imports = [
    'fury', 'numpy', 'abc', 'ABC', 'ABCMeta', 'abstractmethod']
