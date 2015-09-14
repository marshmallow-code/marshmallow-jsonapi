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
    :param dict url_kwargs: Dictionary of keyword arguments passed to `url_for` when
        serializing this field. String arguments enclosed in `< >` will be
        interpreted as attributes to pull from the target object.
    :param bool include_data: Whether to include a resource linkage
        (http://jsonapi.org/format/#document-resource-object-linkage) in the serialized resuult.
    :param bool many: Whether the relationship represents a many-to-one or many-to-many
        relationship.
    :param str type_: The type of resource.
    :param str id_field: Attribute name to pull ids from if a resource linkage is included.
    """
    def __init__(self, endpoint, **kwargs):
        self.endpoint = endpoint
        super(HyperlinkRelated, self).__init__(**kwargs)

    def get_url(self, obj):
        kwargs = resolve_params(obj, self.url_kwargs)
        kwargs['endpoint'] = self.endpoint
        return flask.url_for(**kwargs)
