# -*- coding: utf-8 -*-
# flake8: noqa
import sys

PY2 = int(sys.version_info[0]) == 2

if PY2:
    basestring = basestring
    iteritems = lambda d: d.iteritems()
else:
    basestring = (str, bytes)
    iteritems = lambda d: d.items()
