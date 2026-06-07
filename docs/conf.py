import os
import sys

project = 'QdcEm'
copyright = '2025, Seyed Navid Elyasi'
author = 'Seyed Navid Elyasi'
release = '1.0'

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Logo shown in the top-left sidebar
html_logo = "_static/demo.png"

# Icon shown in the browser tab / next to the URL
html_favicon = "_static/demo.png"

html_theme_options = {
    "logo_only": True,
    "display_version": True,
}

html_theme_options = {
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 3,
    'includehidden': True,
    'titles_only': False,
}
