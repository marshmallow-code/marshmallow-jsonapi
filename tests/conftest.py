# -*- coding: utf-8 -*-
import pytest

from tests.base import Author, Post, Comment, fake

def make_author():
    return Author(id=fake.random_int(), first_name=fake.first_name(),
                    last_name=fake.last_name(), twitter=fake.domain_word())

def make_post():
    comments = [make_comment() for _ in range(2)]
    author = make_author()
    return Post(
        id=fake.random_int(),
        title=fake.catch_phrase(),
        author=author,
        comments=comments)

def make_comment():
    return Comment(id=fake.random_int(), body=fake.bs())

@pytest.fixture()
def author():
    return make_author()

@pytest.fixture()
def authors():
    return [make_author() for _ in range(3)]

@pytest.fixture()
def post():
    return make_post()
