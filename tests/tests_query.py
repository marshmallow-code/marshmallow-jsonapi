import pytest

from marshmallow_jsonapi import query_fields as qf
from marshmallow import fields


class MockRequest:
    """
    A fake request object that has only a query string
    """

    def __init__(self, query):
        self.query_string = query


class TestQueryParser:
    def test_nested_field(self):
        """
        Check that the query string parser can do what JSON API demands of it: parsing `param[key]` into a dictionary
        """
        parser = qf.NestedQueryParserMixin()
        request = MockRequest('include=author&fields[articles]=title,body,author&fields[people]=name')

        assert parser.parse_querystring(request, 'include', None) == 'author'
        assert parser.parse_querystring(request, 'fields', None) == {
            'articles': 'title,body,author',
            'people': 'name'
        }


@pytest.mark.parametrize(
    ('field', 'serialized', 'deserialized'),
    (
            (qf.SortField(), 'title', qf.SortItem(field='title', direction=qf.SortDirection.ASCENDING)),
            (qf.SortField(), '-title', qf.SortItem(field='title', direction=qf.SortDirection.DESCENDING)),
            (qf.Include(), 'author,comments.author', ['author', 'comments.author']),
            (qf.Fields(), {'articles': 'title,body', 'people': 'name'},
             {'articles': ['title', 'body'], 'people': ['name']}
             ),
            (qf.Sort(), '-created,title', [
                qf.SortItem(field='created', direction=qf.SortDirection.DESCENDING),
                qf.SortItem(field='title', direction=qf.SortDirection.ASCENDING)
            ]),
            (qf.PagePagination(), {'number': 3, 'size': 1}, {'number': 3, 'size': 1}),
            (qf.OffsetPagination(), {'offset': 3, 'limit': 1}, {'offset': 3, 'limit': 1}),
            (qf.CursorPagination(fields.Integer()), {'cursor': -1}, {'cursor': -1}),  # A Twitter-api style cursor
    )
)
def test_serialize_deserialize_field(field, serialized, deserialized):
    """
    Tests all new fields, ensuring they serialize and deserialize as expected
    :param field:
    :param serialized:
    :param deserialized:
    :return:
    """
    assert field.serialize('some_field', dict(some_field=deserialized)) == serialized
    assert field.deserialize(serialized) == deserialized


class TestPagePaginationSchema:
    def test_validate(self):
        schema = qf.PagePaginationSchema()
        assert schema.validate({
            'number': 3,
            'size': 1
        }) == {}


class TestOffsetPagePaginationSchema:
    def test_validate(self):
        schema = qf.OffsetPaginationSchema()
        assert schema.validate({
            'offset': 3,
            'limit': 1
        }) == {}

# TODO: Add tests that use an entire schema, not just single fields
