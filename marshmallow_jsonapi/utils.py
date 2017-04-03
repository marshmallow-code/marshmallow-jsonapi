# -*- coding: utf-8 -*-
"""Utility functions.

This module should be considered private API.
"""
import re

import marshmallow
from marshmallow.compat import iteritems
from marshmallow.utils import get_value as _get_value, missing

_MARSHMALLOW_VERSION_INFO = tuple(
    [int(part) for part in marshmallow.__version__.split('.') if part.isdigit()]
)

if _MARSHMALLOW_VERSION_INFO[0] >= 3:
    get_value = _get_value
else:
    def get_value(obj, attr, *args, **kwargs):
        return _get_value(attr, obj, *args, **kwargs)

_tpl_pattern = re.compile(r'\s*<\s*(\S*)\s*>\s*')
def tpl(val):
    """Return value within ``< >`` if possible, else return ``None``."""
    match = _tpl_pattern.match(val)
    if match:
        return match.groups()[0]
    return None

def resolve_params(obj, params, default=missing):
    """Given a dictionary of keyword arguments, return the same dictionary except with
    values enclosed in `< >` resolved to attributes on `obj`.
    """
    param_values = {}
    for name, attr_tpl in iteritems(params):
        attr_name = tpl(str(attr_tpl))
        if attr_name:
            attribute_value = get_value(obj, attr_name, default=default)
            if attribute_value is not missing:
                param_values[name] = attribute_value
            else:
                raise AttributeError(
                    '{attr_name!r} is not a valid '
                    'attribute of {obj!r}'.format(attr_name=attr_name, obj=obj)
                )
        else:
            param_values[name] = attr_tpl
    return param_values
