# -*- coding: utf-8 -*-
from faker import Factory
from marshmallow_jsonapi.utils import _MARSHMALLOW_VERSION_INFO

fake = Factory.create()

def unpack(return_value):
    return return_value.data if _MARSHMALLOW_VERSION_INFO[0] < 3 else return_value

class Bunch(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

class Post(Bunch):
    pass

class Author(Bunch):
    pass

class Comment(Bunch):
    pass

class Keyword(Bunch):
    pass
