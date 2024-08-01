# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# bundled extensions
sys.path.append(os.path.abspath("ext"))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'StArMap Client'
copyright = '2023, Jonathan Gangi'
author = 'Jonathan Gangi'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    # own extensions in 'ext' dir
    "attr_types",
    "attr_index",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    "description": "A client library to communicate with StArMap",
    "extra_nav_links": {
        "Source": "https://github.com/release-engineering/starmap-client",
        "Index": "genindex.html",
    },
    # default is 940px which seems to be a little too small to display 88 chars code
    "page_width": "1100px",
}

html_static_path = ['_static']

html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
        "donate.html",
    ]
}


# -- Extension configuration -------------------------------------------------
autoclass_content = "class"
autodoc_member_order = "bysource"
autodoc_inherit_docstrings = False
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "attrs": ("https://www.attrs.org/en/stable/", None),
}
