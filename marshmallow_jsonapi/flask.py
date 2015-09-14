# -*- coding: utf-8 -*-
"""Flask integration, including a field for linking to related resources."""
from __future__ import absolute_import

import flask
from .fields import HyperlinkRelated as BaseHyperlinkRelated
from .utils import resolve_params

class HyperlinkRelated(BaseHyperlinkRelated):
    """Field which serializes to a "relationship object"
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

    This field is read-only by default.

    :param str endpoint: Name of the Flask endpoint for the related resource.
    :param **kwargs: Same keyword arguments as `marshmallow_jsonapi.fields.HyperlinkRelated`.
    """
    def __init__(self, endpoint, **kwargs):
        self.endpoint = endpoint
        super(HyperlinkRelated, self).__init__(**kwargs)

    def get_url(self, obj):
        kwargs = resolve_params(obj, self.url_kwargs)
        kwargs['endpoint'] = self.endpoint
        return flask.url_for(**kwargs)
