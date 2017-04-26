# -*- coding: utf-8 -*-
from flask import Flask, url_for
import pytest
from werkzeug.routing import BuildError

from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

@pytest.yield_fixture()
def app():
    app_ = Flask('testapp')
    app_.config['DEBUG'] = True
    app_.config['TESTING'] = True

    @app_.route('/posts/')
    def posts():
        return 'All posts'

    @app_.route('/posts/<post_id>/')
    def post_detail(post_id):
        return 'Detail for post {}'.format(post_id)

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


class TestSchema:

    class PostFlaskSchema(Schema):
        id = fields.Int()
        title = fields.Str()

        class Meta:
            type_ = 'posts'
            self_view = 'post_detail'
            self_view_kwargs = {'post_id': '<id>'}
            self_view_many = 'posts'

    class PostAuthorFlaskSchema(Schema):
        id = fields.Int()
        title = fields.Str()

        field = Relationship(
            related_view='author_detail',
            related_view_kwargs={'author_id': '<author.last_name>'},
            default=None
        )

        class Meta:
            type_ = 'posts'
            self_view = 'post_detail'
            self_view_kwargs = {'post_id': '<id>'}
            self_view_many = 'posts'

    def test_schema_requires_view_options(self, post):
        with pytest.raises(ValueError):
            class InvalidFlaskMetaSchema(Schema):
                id = fields.Int()

                class Meta:
                    type_ = 'posts'
                    self_url = '/posts/{id}'
                    self_url_kwargs = {'post_id': '<id>'}

    def test_non_existing_view(self, app, post):
        class InvalidFlaskMetaSchema(Schema):
            id = fields.Int()

            class Meta:
                type_ = 'posts'
                self_view = 'wrong_view'
                self_view_kwargs = {'post_id': '<id>'}

        with pytest.raises(BuildError):
            InvalidFlaskMetaSchema().dump(post).data

    def test_self_link_single(self, app, post):
        data = self.PostFlaskSchema().dump(post).data
        assert 'links' in data
        assert data['links']['self'] == '/posts/{}/'.format(post.id)

    def test_self_link_many(self, app, posts):
        data = self.PostFlaskSchema(many=True).dump(posts).data
        assert 'links' in data
        assert data['links']['self'] == '/posts/'

        assert 'links' in data['data'][0]
        assert data['data'][0]['links']['self'] == '/posts/{}/'.format(posts[0].id)

    def test_schema_with_empty_relationship(self, app, post_with_null_author):
        data = self.PostAuthorFlaskSchema().dump(post_with_null_author).data
        assert 'relationships' not in data


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

    def test_include_resource_linkage_requires_type(self, app, post):
        with pytest.raises(ValueError) as excinfo:
            Relationship(
                related_view='posts_comments',
                related_view_kwargs={'post_id': '<id>'},
                include_resource_linkage=True
            )
        assert excinfo.value.args[0] == 'include_resource_linkage=True requires the type_ argument.'

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

    def test_empty_relationship_with_alternative_identifier_field(self, app, post_with_null_author):
        field = Relationship(
            related_view='author_detail',
            related_view_kwargs={'author_id': '<author.last_name>'},
            default=None
        )
        result = field.serialize('author', post_with_null_author)

        assert not result
