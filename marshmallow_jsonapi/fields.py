# -*- coding: utf-8 -*-
# Make core fields importable from marshmallow_jsonapi
from marshmallow.fields import *  # noqa

class BaseHyperlink(Field):
    """Base hyperlink field. This is used by `marshmallow_jsonapi.Schema` to determine
    Which fields should be formatted as relationship objects.
    """
    pass
