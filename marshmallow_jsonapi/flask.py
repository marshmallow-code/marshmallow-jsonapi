# -*- coding: utf-8 -*-
"""Flask integration, including a field for linking to related resources."""
from __future__ import absolute_import

import flask
from .fields import BaseHyperlink
from .utils import resolve_params, get_value_or_raise

class HyperlinkRelated(BaseHyperlink):
    """Read-only field which serializes to a "relationship object"
    with a "related resource link".

    See: http://jsonapi.org/format/#document-resource-object-relationships

    Examples: ::

        author = HyperlinkRelated(
            endpoint='author_detail',
            url_kwargs={'author_id': '<author.id>'},
        )

        comments = HyperlinkRelated(
            endpoint='posts_comments',
            url_kwargs={'post_id': '<id>'},
            many=True, include_data=True,
            type_='comments'
        )


    :param str endpoint: Name of the Flask endpoint for the related resource.
    :param dict url_kwargs: Dictionary of keyword arguments passed to `url_for` when
        serializing this field. String arguments enclosed in `< >` will be
        interpreted as attributes to pull from the object.
    """
    id_field = 'id'

    def __init__(self, endpoint, url_kwargs=None, many=False,
                include_data=False, type_=None, id_field=None, **kwargs):
        self.endpoint = endpoint
        self.url_kwargs = url_kwargs or {}
        if include_data and not type_:
            raise ValueError('include_data=True requires the type_ argument.')
        self.many = many
        self.include_data = include_data
        self.type_ = type_
        self.id_field = id_field or self.id_field
        self.dump_only = kwargs.pop('dump_only', True)
        super(HyperlinkRelated, self).__init__(**kwargs)

    def get_url(self, obj):
        kwargs = resolve_params(obj, self.url_kwargs)
        kwargs['endpoint'] = self.endpoint
        return flask.url_for(**kwargs)

    def _serialize(self, value, attr, obj):
        dict_class = self.parent.dict_class if self.parent else dict
        ret = dict_class()
        ret[attr] = dict_class()
        ret[attr]['links'] = dict_class()
        ret[attr]['links']['related'] = self.get_url(obj)
        if self.include_data:
            ret[attr]['data'] = dict_class()
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

            ret[attr]['data'] = included_data
        return ret
