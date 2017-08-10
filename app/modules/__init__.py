# encoding: utf-8
"""
Modules
=======

Modules enable logical resource separation.

You may control enabled modules by modifying ``ENABLED_MODULES`` config
variable.
"""
import settings

#this will launch every modules you have referenced as active

def init_app(app, **kwargs):
    from importlib import import_module

    for module_name in settings.ENABLED_MODULES:
        import_module('.%s' % module_name, package=__name__).init_app(app, **kwargs)
