# -*- coding: utf-8 -*-
"""Flask integration, including a field for linking to related resources."""
from __future__ import absolute_import

import flask
from werkzeug.routing import BuildError

from .fields import Relationship as GenericRelationship
from .utils import resolve_params

class Relationship(GenericRelationship):
    """Field which serializes to a "relationship object"
    with a "related resource link".

    See: http://jsonapi.org/format/#document-resource-object-relationships

    Examples: ::

        author = Relationship(
            related_view='author_detail',
            related_view_kwargs={'author_id': '<author.id>'},
        )

        comments = Relationship(
            related_view='posts_comments',
            related_view_kwargs={'post_id': '<id>'},
            many=True, include_resource_linkage=True,
            type_='comments'
        )

    This field is read-only by default.

    :param str related_view: View name for related resource link.
    :param dict related_view_kwargs: Path kwargs fields for `related_view`. String arguments
        enclosed in `< >` will be interpreted as attributes to pull from the target object.
    :param str self_view: View name for self relationship link.
    :param dict self_view_kwargs: Path kwargs for `self_view`. String arguments
        enclosed in `< >` will be interpreted as attributes to pull from the target object.
    :param **kwargs: Same keyword arguments as `marshmallow_jsonapi.fields.Relationship`.
    """
    def __init__(
        self,
        related_view=None, related_view_kwargs=None,
        self_view=None, self_view_kwargs=None,
        **kwargs
    ):
        self.related_view = related_view
        self.related_view_kwargs = related_view_kwargs or {}
        self.self_view = self_view
        self.self_view_kwargs = self_view_kwargs or {}
        super(Relationship, self).__init__(**kwargs)

    def get_url(self, obj, view_name, view_kwargs):
        if view_name:
            kwargs = resolve_params(obj, view_kwargs)
            kwargs['endpoint'] = view_name
            try:
                return flask.url_for(**kwargs)
            except BuildError:
                if None in kwargs.values():  # most likely to be caused by empty relationship
                    return None
                raise
        return None

    def get_related_url(self, obj):
        return self.get_url(obj, self.related_view, self.related_view_kwargs)

    def get_self_url(self, obj):
        return self.get_url(obj, self.self_view, self.self_view_kwargs)
