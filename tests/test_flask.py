# -*- coding: utf-8 -*-
from flask import Flask, url_for
import pytest

from marshmallow_jsonapi.flask import HyperlinkRelated

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

class TestHyperlinkRelated:

    def test_serialize_basic(self, app, post):
        field = HyperlinkRelated(
            endpoint='posts_comments',
            url_kwargs={'post_id': '<id>'},
        )
        result = field.serialize('comments', post)
        assert 'comments' in result
        related = result['comments']['links']['related']
        assert related == url_for('posts_comments', post_id=post.id)

    def test_serialize_external(self, app, post):
        field = HyperlinkRelated(
            endpoint='posts_comments',
            url_kwargs={'post_id': '<id>', '_external': True},
        )
        result = field.serialize('comments', post)
        related = result['comments']['links']['related']
        assert related == url_for('posts_comments', post_id=post.id, _external=True)

    def test_include_data_requires_type(self, app, post):
        with pytest.raises(ValueError) as excinfo:
            HyperlinkRelated(
                endpoint='posts_comments',
                url_kwargs={'post_id': '<id>'},
                include_data=True
            )
        assert excinfo.value.args[0] == 'include_data=True requires the type_ argument.'

    def test_is_dump_only_by_default(self):
        field = HyperlinkRelated(
            'author_detail',
            url_kwargs={'author_id': '<id>'}
        )
        assert field.dump_only is True
