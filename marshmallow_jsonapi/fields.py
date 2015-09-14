# -*- coding: utf-8 -*-
"""Includes all the fields classes from `marshmallow.fields` as well as
fields for serializing JSON API-formatted hyperlinks.
"""
# Make core fields importable from marshmallow_jsonapi
from marshmallow.fields import *  # noqa

from .utils import resolve_params, get_value_or_raise

class BaseHyperlink(Field):
    """Base hyperlink field. This is used by `marshmallow_jsonapi.Schema` to determine
    which fields should be formatted as relationship objects.
    """
    pass


class HyperlinkRelated(BaseHyperlink):
    """Framework-independent field which serializes to a "relationship object" with a
    "related resource link".

    See: http://jsonapi.org/format/#document-resource-object-relationships

    Examples: ::

        author = HyperlinkRelated(
            '/authors/{author_id}',
            url_kwargs={'author_id': '<author.id>'},
        )

        comments = HyperlinkRelated(
            '/posts/{post_id}/comments',
            url_kwargs={'post_id': '<id>'},
            many=True, include_data=True,
            type_='comments'
        )

    This field is read-only by default.

    :param str template: Format string for the URL.
    :param dict url_kwargs: Replacement fields for `template`. String arguments enclosed in `< >`
        will be interpreted as attributes to pull from the target object.
    :param bool include_data: Whether to include a resource linkage
        (http://jsonapi.org/format/#document-resource-object-linkage) in the serialized result.
    :param bool many: Whether the relationship represents a many-to-one or many-to-many
        relationship. Only affects serialization of the resource linkage.
    :param str type_: The type of resource.
    :param str id_field: Attribute name to pull ids from if a resource linkage is included.
    """

    id_field = 'id'

    def __init__(self, template='', url_kwargs=None, include_data=False,
            many=False, type_=None, id_field=None, **kwargs):
        self.template = template
        self.url_kwargs = url_kwargs or {}
        if include_data and not type_:
            raise ValueError('include_data=True requires the type_ argument.')
        self.many = many
        self.include_data = include_data
        self.type_ = type_
        self.id_field = id_field or self.id_field
        super(HyperlinkRelated, self).__init__(**kwargs)
        self.dump_only = kwargs.pop('dump_only', True)

    def get_url(self, obj):
        kwargs = resolve_params(obj, self.url_kwargs)
        return self.template.format(**kwargs)

    def add_resource_linkage(self, value):
        if self.many:
            included_data = [
                {'type': self.type_,
                    'id': get_value_or_raise(self.id_field, each)}
                for each in value
            ]
        else:
            included_data = {
                'type': self.type_,
                'id': get_value_or_raise(self.id_field, value)
            }
        return included_data

    def _serialize(self, value, attr, obj):
        dict_class = self.parent.dict_class if self.parent else dict
        ret = dict_class()
        ret[attr] = dict_class()
        ret[attr]['links'] = dict_class()
        ret[attr]['links']['related'] = self.get_url(obj)
        if self.include_data:
            ret[attr]['data'] = self.add_resource_linkage(value)
        return ret
