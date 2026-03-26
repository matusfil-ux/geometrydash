"""Script setting sphinx configuration."""

from os.path import abspath
from sys import path


# doc theme
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "sidebarwidth": 400,
}

# autodoc options
autodoc_default_options = {
    "members": True,
    "special-members": "__call__",
}

# doc extensions
extensions = [
    "numpydoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax",
    "sphinx_rtd_size",
]

# set width of HTML page using extension sphinx_rtd_size
sphinx_rtd_size_width = "100%"

# doc parameters
numfig = True

# project details for docs
project = "Python Poetry Template"
version = "2.1.0"

# insert path to source code
path.insert(0, abspath(".."))
