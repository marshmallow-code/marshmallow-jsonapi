# -*- coding: utf-8 -*-
import pytest

from marshmallow import ValidationError
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

        assert result['author']['data']['id'] == str(post.author.id)

    def test_include_data_single_foreign_key(self, post):
        field = Relationship(
            related_url='/posts/{post_id}/author/',
            related_url_kwargs={'post_id': '<id>'},
            include_data=True, type_='people'
        )
        result = field.serialize('author_id', post)
        assert result['author_id']['data']['id'] == str(post.author_id)

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
        assert ids == [str(each.id) for each in post.comments]

    def test_deserialize_data_single(self, post):
        field = Relationship(
            related_url='/posts/{post_id}/comments',
            related_url_kwargs={'post_id': '<id>'},
            many=False, include_data=True, type_='comments'
        )
        value = {'data': {'type': 'comments', 'id': '1'}}
        result = field.deserialize(value)
        assert result == '1'

    def test_deserialize_data_many(self, post):
        field = Relationship(
            related_url='/posts/{post_id}/comments',
            related_url_kwargs={'post_id': '<id>'},
            many=True, include_data=True, type_='comments'
        )
        value = {'data': [{'type': 'comments', 'id': '1'}]}
        result = field.deserialize(value)
        assert result == ['1']

    def test_deserialize_data_missing_id(self, post):
        field = Relationship(
            related_url='/posts/{post_id}/comments',
            related_url_kwargs={'post_id': '<id>'},
            many=False, include_data=True, type_='comments'
        )
        with pytest.raises(ValidationError) as excinfo:
            value = {'data': {'type': 'comments'}}
            field.deserialize(value)
        assert excinfo.value.args[0] == ['Must have an `id` field']

    def test_deserialize_data_missing_type(self, post):
        field = Relationship(
            related_url='/posts/{post_id}/comments',
            related_url_kwargs={'post_id': '<id>'},
            many=False, include_data=True, type_='comments'
        )
        with pytest.raises(ValidationError) as excinfo:
            value = {'data': {'id': '1'}}
            field.deserialize(value)
        assert excinfo.value.args[0] == ['Must have a `type` field']

    def test_deserialize_data_incorrect_type(self, post):
        field = Relationship(
            related_url='/posts/{post_id}/comments',
            related_url_kwargs={'post_id': '<id>'},
            many=False, include_data=True, type_='comments'
        )
        with pytest.raises(ValidationError) as excinfo:
            value = {'data': {'type': 'posts', 'id': '1'}}
            field.deserialize(value)
        assert excinfo.value.args[0] == ['Invalid `type` specified']

    def test_deserialize_null_data_value(self, post):
        field = Relationship(
            related_url='/posts/{post_id}/comments',
            related_url_kwargs={'post_id': '<id>'},
            many=False, include_data=False, type_='comments'
        )
        result = field.deserialize({'data': None})
        assert result is None

    def test_deserialize_empty_data_list(self, post):
        field = Relationship(
            related_url='/posts/{post_id}/comments',
            related_url_kwargs={'post_id': '<id>'},
            many=False, include_data=False, type_='comments'
        )
        result = field.deserialize({'data': []})
        assert result == []

    def test_deserialize_empty_data_node(self, post):
        field = Relationship(
            related_url='/posts/{post_id}/comments',
            related_url_kwargs={'post_id': '<id>'},
            many=False, include_data=False, type_='comments'
        )
        with pytest.raises(ValidationError) as excinfo:
            field.deserialize({'data': {}})
        assert excinfo.value.args[0] == [
            'Must have an `id` field', 'Must have a `type` field']

    def test_deserialize_empty_relationship_node(self, post):
        field = Relationship(
            related_url='/posts/{post_id}/comments',
            related_url_kwargs={'post_id': '<id>'},
            many=False, include_data=False, type_='comments'
        )
        with pytest.raises(ValidationError) as excinfo:
            field.deserialize({})
        assert excinfo.value.args[0] == 'Must include a `data` key'

    def test_include_null_data_single(self, post_with_null_author):
        field = Relationship(
            related_url='posts/{post_id}/author',
            related_url_kwargs={'post_id': '<id>'},
            include_data=True, type_='people'
        )
        result = field.serialize('author', post_with_null_author)
        assert result['author'] and result['author']['links']['related']
        assert result['author']['data'] is None

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
