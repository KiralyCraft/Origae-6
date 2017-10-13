
from __future__ import absolute_import

from origae.utils import subclass


@subclass
class Error(Exception):
    pass


@subclass
class BadNetworkError(Error):
    """
    Errors that occur when validating a network
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


@subclass
class NetworkVisualizationError(Error):
    """
    Errors that occur when validating a network
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
