# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2].resolve()))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'CoNLL-U Tools'
copyright = '%Y, Gabe Pizzorno'
author = 'Gabe Pizzorno'
release = '1.3.0'
version = '1.3.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.githubpages',
    'sphinxcontrib.mermaid',
    'sphinx_autodoc_typehints',
    'myst_parser',
]

source_suffix = ['.rst', '.md']

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
}

autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'

# Napoleon settings (for Google/NumPy style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Autosummary settings
autosummary_generate = True
autosummary_imported_members = False

# MyST settings (Markdown support)
myst_enable_extensions = [
    'attrs_inline',
    'colon_fence',
    'deflist',
    'dollarmath',
    'fieldlist',
    'html_admonition',
    'html_image',
    'replacements',
    'smartquotes',
    'strikethrough',
    'substitution',
    'tasklist',
]
myst_heading_anchors = 3


# Intersphinx settings (cross-reference external docs)
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
}

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_theme_options = {
    'analytics_id': '',
    'logo_only': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
}

html_context = {
    'display_github': True,
    'github_user': 'gpizzorno',
    'github_repo': 'conllu_tools',
    'github_version': 'main',
    'conf_py_path': '/docs/source/',
}

html_title = f'{project} v{version}'
html_short_title = 'CoNLL-U Tools'
html_favicon = None
html_logo = None

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False
# If true, "Created using Sphinx" is shown in the HTML footer.
html_show_sphinx = False
# If true, "(C) Copyright ..." is shown in the HTML footer.
html_show_copyright = True

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass).
latex_documents = [
    ('index', 'conllu_tools.tex', 'CoNLL-U Tools Documentation', 'Gabe Pizzorno', 'manual'),
]

# -- Options for manual page output -----------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'conllu_tools', 'CoNLL-U Tools Documentation', [author], 1),
]

# -- Options for Texinfo output ---------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        'index',
        'CoNLLUTools',
        'CoNLL-U Tools Documentation',
        author,
        'CoNLLUTools',
        'Tools for working with CoNLL-U files, UD treebanks, and annotated corpora.',
        'Miscellaneous',
    ),
]

# -- Extension configuration -------------------------------------------------

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
