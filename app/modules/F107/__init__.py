# encoding: utf-8
"""
This module is here so you have the minimum requirement for building a layout, feel free to modify or delete it
"""
from extensions.api import api
from . import resources

def init_app(app, **kwargs):
    api.add_namespace(resources.api)