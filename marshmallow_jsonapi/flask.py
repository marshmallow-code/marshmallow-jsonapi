"""Flask integration that avoids the need to hard-code URLs for links.

This includes a Flask-specific schema with custom Meta options and a
relationship field for linking to related resources.
"""
import flask
from werkzeug.routing import BuildError

from .fields import Relationship as GenericRelationship
from .schema import Schema as DefaultSchema, SchemaOpts as DefaultOpts
from .utils import resolve_params


class SchemaOpts(DefaultOpts):
    """Options to use Flask view names instead of hard coding URLs."""

    def __init__(self, meta, *args, **kwargs):
        if getattr(meta, "self_url", None):
            raise ValueError(
                "Use `self_view` instead of `self_url` " "using the Flask extension."
            )
        if getattr(meta, "self_url_kwargs", None):
            raise ValueError(
                "Use `self_view_kwargs` instead of `self_url_kwargs` "
                "when using the Flask extension."
            )
        if getattr(meta, "self_url_many", None):
            raise ValueError(
                "Use `self_view_many` instead of `self_url_many` "
                "when using the Flask extension."
            )

        if getattr(meta, "self_view_kwargs", None) and not getattr(
            meta, "self_view", None
        ):
            raise ValueError(
                "Must specify `self_view` Meta option when "
                "`self_view_kwargs` is specified."
            )

        # Transfer Flask options to URL options, to piggy-back on its handling
        meta.self_url = getattr(meta, "self_view", None)
        meta.self_url_kwargs = getattr(meta, "self_view_kwargs", None)
        meta.self_url_many = getattr(meta, "self_view_many", None)

        super().__init__(meta, *args, **kwargs)


class Schema(DefaultSchema):
    """A Flask specific schema that resolves self URLs from view names."""

    OPTIONS_CLASS = SchemaOpts

    class Meta:
        """Options object that takes the same options as `marshmallow-jsonapi.Schema`,
        but instead of ``self_url``, ``self_url_kwargs`` and ``self_url_many``
        has the following options to resolve the URLs from Flask views:

        * ``self_view`` - View name to resolve the self URL link from.
        * ``self_view_kwargs`` - Replacement fields for ``self_view``. String
          attributes enclosed in ``< >`` will be interpreted as attributes to
          pull from the schema data.
        * ``self_view_many`` - View name to resolve the self URL link when a
          collection of resources is returned.
        """

        pass

    def generate_url(self, view_name, **kwargs):
        """Generate URL with any kwargs interpolated."""
        return flask.url_for(view_name, **kwargs) if view_name else None


class Relationship(GenericRelationship):
    r"""Field which serializes to a "relationship object"
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
    :param \*\*kwargs: Same keyword arguments as `marshmallow_jsonapi.fields.Relationship`.
    """

    def __init__(
        self,
        related_view=None,
        related_view_kwargs=None,
        *,
        self_view=None,
        self_view_kwargs=None,
        **kwargs
    ):
        self.related_view = related_view
        self.related_view_kwargs = related_view_kwargs or {}
        self.self_view = self_view
        self.self_view_kwargs = self_view_kwargs or {}
        super().__init__(**kwargs)

    def get_url(self, obj, view_name, view_kwargs):
        if view_name:
            kwargs = resolve_params(obj, view_kwargs, default=self.default)
            kwargs["endpoint"] = view_name
            try:
                return flask.url_for(**kwargs)
            except BuildError:
                if (
                    None in kwargs.values()
                ):  # most likely to be caused by empty relationship
                    return None
                raise
        return None

    def get_related_url(self, obj):
        return self.get_url(obj, self.related_view, self.related_view_kwargs)

    def get_self_url(self, obj):
        return self.get_url(obj, self.self_view, self.self_view_kwargs)
