# -*- coding: utf-8 -*-
import pytest

from marshmallow_jsonapi.fields import HyperlinkRelated


class TestGenericHyperlinkRelated:

    def test_serialize_basic(self, post):
        field = HyperlinkRelated(
            'http://example.com/posts/{id}/comments',
            url_kwargs={'id': '<id>'}
        )
        result = field.serialize('comments', post)
        assert field.serialize('comments', post)
        related = result['comments']['links']['related']
        assert related == 'http://example.com/posts/{id}/comments'.format(id=post.id)

    def test_include_data_requires_type(self, post):
        with pytest.raises(ValueError) as excinfo:
            HyperlinkRelated(
                template='/posts/{post_id}',
                url_kwargs={'post_id': '<id>'},
                include_data=True
            )
        assert excinfo.value.args[0] == 'include_data=True requires the type_ argument.'

    def test_include_data_single(self, post):
        field = HyperlinkRelated(
            template='/authors/{author_id}',
            url_kwargs={'author_id': '<author.id>'},
            include_data=True, type_='people'
        )
        result = field.serialize('author', post)
        assert 'data' in result['author']
        assert result['author']['data']

        assert result['author']['data']['id'] == post.author.id

    def test_include_data_many(self, post):
        field = HyperlinkRelated(
            template='/posts/{post_id}/comments',
            url_kwargs={'post_id': '<id>'},
            many=True, include_data=True, type_='comments'
        )
        result = field.serialize('comments', post)
        assert 'data' in result['comments']
        assert result['comments']['data']
        ids = [each['id'] for each in result['comments']['data']]
        assert ids == [each.id for each in post.comments]

    def test_is_dump_only_by_default(self):
        field = HyperlinkRelated(
            'http://example.com/posts/{id}/comments',
            url_kwargs={'id': '<id>'}
        )
        assert field.dump_only is True
