#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
shoplift.exceptions
-------------------

All exceptions used inside shoplift
"""



class ShopliftException(Exception):
    """Base exception. All Shoplift exceptions inherit this class."""

class ConfigDoesNotExistException(ShopliftException):
    """Raised when the specified configuration file path cannot be found"""

