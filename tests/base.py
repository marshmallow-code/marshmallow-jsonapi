# -*- coding: utf-8 -*-
from faker import Factory

fake = Factory.create()

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
