# -*- coding: utf-8 -*-
# Ambry Bundle Library File
# Use this file for code that may be imported into other bundles


def dot_to_none(v):
    """ Convert dots to NULLs"""
    if isinstance(v, basestring) and v.strip() == '.':
        return None
    return v


def illegal_to_none(v):
    """ Converts '9 8   ' value from mrace field to None. """
    if isinstance(v, basestring) and v == '9 8   ':
        return None
    return v
