import os
import sys

project = 'QdcEm'
copyright = '2025, Seyed Navid Elyasi, Paolo Monti, Jun Li, Rui Lin'
author = 'Seyed Navid Elyasi, Paolo Monti, Jun Li, Rui Lin'
release = '1.0'

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

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
