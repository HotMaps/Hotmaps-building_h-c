# encoding: utf-8
"""
Extended Api implementation with an application-specific helpers
----------------------------------------------------------------
"""

from flask_restplus_patched import Api as BaseApi

from flask_restplus_patched import Namespace

class Api(BaseApi):
    """
    Having app-specific handlers here.
    """

    def namespace(self, *args, **kwargs):
        # The only purpose of this method is to pass custom Namespace class
        _namespace = Namespace(*args, **kwargs)
        self.namespaces.append(_namespace)
        return _namespace
