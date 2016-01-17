# -*- coding: utf-8 -*-
import pytest

from marshmallow_jsonapi.fields import Relationship


class TestGenericRelationshipField:

    def test_serialize_relationship_link(self, post):
        field = Relationship(
            'http://example.com/posts/{id}/comments',
            related_url_kwargs={'id': '<id>'}
        )
        result = field.serialize('comments', post)
        assert field.serialize('comments', post)
        related = result['comments']['links']['related']
        assert related == 'http://example.com/posts/{id}/comments'.format(id=post.id)

    def test_serialize_self_link(self, post):
        field = Relationship(
            self_url='http://example.com/posts/{id}/relationships/comments',
            self_url_kwargs={'id': '<id>'}
        )
        result = field.serialize('comments', post)
        assert field.serialize('comments', post)
        related = result['comments']['links']['self']
        assert 'related' not in result['comments']['links']
        assert related == 'http://example.com/posts/{id}/relationships/comments'.format(id=post.id)

    def test_include_data_requires_type(self, post):
        with pytest.raises(ValueError) as excinfo:
            Relationship(
                related_url='/posts/{post_id}',
                related_url_kwargs={'post_id': '<id>'},
                include_data=True
            )
        assert excinfo.value.args[0] == 'include_data=True requires the type_ argument.'

    def test_include_data_single(self, post):
        field = Relationship(
            related_url='/posts/{post_id}/author/',
            related_url_kwargs={'post_id': '<id>'},
            include_data=True, type_='people'
        )
        result = field.serialize('author', post)
        assert 'data' in result['author']
        assert result['author']['data']

        assert result['author']['data']['id'] == post.author.id

    def test_include_data_many(self, post):
        field = Relationship(
            related_url='/posts/{post_id}/comments',
            related_url_kwargs={'post_id': '<id>'},
            many=True, include_data=True, type_='comments'
        )
        result = field.serialize('comments', post)
        assert 'data' in result['comments']
        assert result['comments']['data']
        ids = [each['id'] for each in result['comments']['data']]
        assert ids == [each.id for each in post.comments]

    def test_include_null_data_single(self, post_with_null_author):
        field = Relationship(
            related_url='posts/{post_id}/author',
            related_url_kwargs={'post_id': '<id>'},
            include_data=True, type_='people'
        )
        result = field.serialize('author', post_with_null_author)
        assert result['author'] and result['author']['links']['related']
        assert result['author']['data'] == None

    def test_include_null_data_many(self, post_with_null_comment):
        field = Relationship(
            related_url='/posts/{post_id}/comments',
            related_url_kwargs={'post_id': '<id>'},
            many=True, include_data=True, type_='comments'
        )
        result = field.serialize('comments', post_with_null_comment)
        assert result['comments'] and result['comments']['links']['related']
        assert result['comments']['data'] == []

    def test_exclude_data(self, post_with_null_comment):
        field = Relationship(
            related_url='/posts/{post_id}/comments',
            related_url_kwargs={'post_id': '<id>'},
            many=True, include_data=False, type_='comments'
        )
        result = field.serialize('comments', post_with_null_comment)
        assert result['comments'] and result['comments']['links']['related']
        assert 'data' not in result['comments']

    def test_is_dump_only_by_default(self):
        field = Relationship(
            related_url='http://example.com/posts/{id}/comments',
            related_url_kwargs={'id': '<id>'}
        )
        assert field.dump_only is True

    def test_deserialize_relationship_single(self):
        field = Relationship(
            related_url='/posts/{post_id}/author/',
            related_url_kwargs={'post_id': '<id>'},
            include_data=True, type_='people'
        )
        val = 1
        result = field.deserialize(val)
        assert result == val

    def test_deserialize_relationship_many(self):
        with pytest.raises(ValueError) as excinfo:
            Relationship(
                related_url='/posts/{post_id}/comments',
                related_url_kwargs={'post_id': '<id>'},
                many=True, include_data=False, type_='comments',
                dump_only=False
            )
        assert excinfo.value.args[0] == 'Loading is not supported for many=True.'

    def test_deserialize_null_relationship(self):
        field = Relationship(
            related_url='/posts/{post_id}/author/',
            related_url_kwargs={'post_id': '<id>'},
            include_data=True, type_='people', missing=None,
        )
        val = None
        result = field.deserialize(val)
        assert result == val
