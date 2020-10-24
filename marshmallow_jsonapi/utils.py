"""Utility functions.

This module should be considered private API.
"""
import re

from marshmallow.utils import get_value, missing


_tpl_pattern = re.compile(r"\s*<\s*(\S*)\s*>\s*")


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
    for name, attr_tpl in params.items():
        attr_name = tpl(str(attr_tpl))
        if attr_name:
            attribute_value = get_value(obj, attr_name, default=default)
            if attribute_value is not missing:
                param_values[name] = attribute_value
            else:
                raise AttributeError(
                    "{attr_name!r} is not a valid "
                    "attribute of {obj!r}".format(attr_name=attr_name, obj=obj)
                )
        else:
            param_values[name] = attr_tpl
    return param_values
