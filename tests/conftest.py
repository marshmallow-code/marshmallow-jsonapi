# -*- coding: utf-8 -*-
import pytest

from tests.base import Author, Post, Comment, fake

def make_author():
    return Author(id=fake.random_int(), first_name=fake.first_name(),
                  last_name=fake.last_name(), twitter=fake.domain_word())

def make_post(with_comments=True, with_author=True):
    comments = [make_comment() for _ in range(2)] if with_comments else []
    author = make_author() if with_author else None
    return Post(
        id=fake.random_int(),
        title=fake.catch_phrase(),
        author=author,
        comments=comments)

def make_post_document(with_comments=True, with_author=True):
    doc = {
        'type': 'posts',
        'id': fake.random_int(),
        'attributes': {
            'title': fake.catch_phrase()
        },
        'relationships': {}
    }
    if with_comments:
        doc['relationships']['comments'] = [
          { 'type': 'comments', 'id': '5' },
          { 'type': 'comments', 'id': '12' }
        ]
    if with_author:
        doc['relationships']['author'] = {
                'data': { 'type': 'people', 'id': 9 }
            }
    return {'data': doc}

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

@pytest.fixture()
def post_with_null_comment():
    return make_post(with_comments=False)

@pytest.fixture()
def post_with_null_author():
    return make_post(with_author=False)

@pytest.fixture()
def post_document():
    return make_post_document(with_comments=False)
