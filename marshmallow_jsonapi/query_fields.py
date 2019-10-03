"""
Includes fields designed solely for parsing query/URL parameters from JSON API requests
"""
import querystring_parser.parser as qsp
from marshmallow import Schema
from webargs import core, fields
from webargs.fields import DelimitedList, String, Dict
from enum import Enum
import typing


class NestedQueryParserMixin:
    """
    Mixin for creating a JSON API-compatible parser from a regular Webargs parser

    Examples: ::
    from marshmallow_jsonapi.query_fields import NestedQueryParserMixin, JsonApiRequestSchema
    from webargs.flaskparser import FlaskParser

        class FlaskJsonApiParser(FlaskParser, NestedQueryParserMixin):
            pass

        parser = FlaskJsonApiParser()

        @parser.use_args(JsonApiRequestSchema())
        def greet(args):
            return 'You requested to include these relationships: ' + ', '.join(args['include'])
    """

    def parse_querystring(self, req, name, field):
        return core.get_value(qsp.parse(req.query_string), name, field)


class SortDirection(Enum):
    """
    The direction to sort a field by
    """
    ASCENDING = 1
    DESCENDING = 2


class SortItem(typing.NamedTuple):
    """
    Represents a single entry in the list of fields to sort by
    """
    field: str
    direction: SortDirection


class SortField(fields.Field):
    """
    Marshmallow field that parses and dumps a JSON API sort parameter
    """

    def _serialize(self, value, attr, obj, **kwargs):
        if value.direction == SortDirection.DESCENDING:
            return '-' + value.field
        else:
            return value.field

    def _deserialize(self, value, attr, data, **kwargs):
        if value.startswith('-'):
            return SortItem(value[1:], SortDirection.DESCENDING)
        else:
            return SortItem(value[1:], SortDirection.ASCENDING)


class PagePaginationSchema(Schema):
    number = fields.Integer()
    size = fields.Integer()


class OffsetPaginationSchema(Schema):
    offset = fields.Integer()
    limit = fields.Integer()


class CursorPaginationSchema(Schema):
    cursor = fields.Raw()


include_param = fields.DelimitedList(String(), data_key='include')
"""
The value of the include parameter MUST be a comma-separated (U+002C COMMA, “,”) list of relationship paths.
A relationship path is a dot-separated (U+002E FULL-STOP, “.”) list of relationship names.

.. seealso::
   `JSON API Specification, Inclusion of Related Resources <https://jsonapi.org/format/#fetching-includes>`_
      JSON API specification for the include request parameter
"""

fields_param = Dict(keys=String(), values=DelimitedList(String()), data_key='fields')
"""
The value of the fields parameter MUST be a comma-separated (U+002C COMMA, “,”) list that refers to the name(s) of
the fields to be returned.

.. seealso::
   `JSON API Specification, Sparse Fieldsets <https://jsonapi.org/format/#fetching-sparse-fieldsets>`_
      JSON API specification for the fields request parameter
"""

sort_param = DelimitedList(SortField(), data_key='sort')
"""
An endpoint MAY support requests to sort the primary data with a sort query parameter.
The value for sort MUST represent sort fields.
An endpoint MAY support multiple sort fields by allowing comma-separated (U+002C COMMA, “,”) sort fields.
Sort fields SHOULD be applied in the order specified.

.. seealso::
   `JSON API Specification, Sorting <https://jsonapi.org/format/#fetching-sorting>`_
      JSON API specification for the sort request parameter
"""

filter_param = Dict(keys=String(), values=DelimitedList(String()), data_key='filter')

page_pagination_param = fields.Nested(PagePaginationSchema(), data_key='page')
offset_pagination_param = fields.Nested(OffsetPaginationSchema(), data_key='page')
cursor_pagination_param = fields.Nested(CursorPaginationSchema(), data_key='page')
