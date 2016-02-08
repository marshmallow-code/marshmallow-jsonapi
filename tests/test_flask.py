# -*- coding: utf-8 -*-
from flask import Flask, url_for
import pytest
from werkzeug.routing import BuildError

from marshmallow_jsonapi.flask import Relationship

@pytest.yield_fixture()
def app():
    app_ = Flask('testapp')
    app_.config['DEBUG'] = True
    app_.config['TESTING'] = True

    @app_.route('/posts/<post_id>/comments/')
    def posts_comments(post_id):
        return 'Comments for post {}'.format(post_id)

    @app_.route('/authors/<int:author_id>')
    def author_detail(author_id):
        return 'Detail for author {}'.format(author_id)

    ctx = app_.test_request_context()
    ctx.push()
    yield app_
    ctx.pop()

class TestRelationshipField:

    def test_serialize_basic(self, app, post):
        field = Relationship(
            related_view='posts_comments',
            related_view_kwargs={'post_id': '<id>'},
        )
        result = field.serialize('comments', post)
        assert 'links' in result
        assert 'related' in result['links']
        related = result['links']['related']
        assert related == url_for('posts_comments', post_id=post.id)

    def test_serialize_external(self, app, post):
        field = Relationship(
            related_view='posts_comments',
            related_view_kwargs={'post_id': '<id>', '_external': True},
        )
        result = field.serialize('comments', post)
        related = result['links']['related']
        assert related == url_for('posts_comments', post_id=post.id, _external=True)

    def test_include_data_requires_type(self, app, post):
        with pytest.raises(ValueError) as excinfo:
            Relationship(
                related_view='posts_comments',
                related_view_kwargs={'post_id': '<id>'},
                include_data=True
            )
        assert excinfo.value.args[0] == 'include_data=True requires the type_ argument.'

    def test_serialize_self_link(self, app, post):
        field = Relationship(
            self_view='posts_comments',
            self_view_kwargs={'post_id': '<id>'},
        )
        result = field.serialize('comments', post)
        assert 'links' in result
        assert 'self' in result['links']
        related = result['links']['self']
        assert related == url_for('posts_comments', post_id=post.id)

    def test_empty_relationship(self, app, post_with_null_author):
        field = Relationship(
            related_view='author_detail',
            related_view_kwargs={'author_id': '<author>'}
        )
        result = field.serialize('author', post_with_null_author)

        assert not result

    def test_non_existing_view(self, app, post):
        field = Relationship(
            related_view='non_existing_view',
            related_view_kwargs={'author_id': '<author>'}
        )
        with pytest.raises(BuildError):
            field.serialize('author', post)
