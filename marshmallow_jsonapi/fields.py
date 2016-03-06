# -*- coding: utf-8 -*-
"""Includes all the fields classes from `marshmallow.fields` as well as
fields for serializing JSON API-formatted hyperlinks.
"""
from marshmallow import ValidationError
# Make core fields importable from marshmallow_jsonapi
from marshmallow.fields import *  # noqa
from marshmallow.utils import get_value, is_collection

from .utils import resolve_params


class BaseRelationship(Field):
    """Base relationship field.

    This is used by `marshmallow_jsonapi.Schema` to determine which
    fields should be formatted as relationship objects.

    See: http://jsonapi.org/format/#document-resource-object-relationships
    """

    pass


class Relationship(BaseRelationship):
    """Framework-independent field which serializes to a "relationship object".

    See: http://jsonapi.org/format/#document-resource-object-relationships

    Examples: ::

        author = Relationship(
            related_url='/authors/{author_id}',
            related_url_kwargs={'author_id': '<author.id>'},
        )

        comments = Relationship(
            related_url='/posts/{post_id}/comments/',
            related_url_kwargs={'post_id': '<id>'},
            many=True, include_data=True,
            type_='comments'
        )

    This field is read-only by default.

    :param str related_url: Format string for related resource links.
    :param dict related_url_kwargs: Replacement fields for `related_url`. String arguments
        enclosed in `< >` will be interpreted as attributes to pull from the target object.
    :param str self_url: Format string for self relationship links.
    :param dict self_url_kwargs: Replacement fields for `self_url`. String arguments
        enclosed in `< >` will be interpreted as attributes to pull from the target object.
    :param bool include_data: Whether to include a resource linkage
        (http://jsonapi.org/format/#document-resource-object-linkage) in the serialized result.
    :param bool many: Whether the relationship represents a many-to-one or many-to-many
        relationship. Only affects serialization of the resource linkage.
    :param str type_: The type of resource.
    :param str id_field: Attribute name to pull ids from if a resource linkage is included.
    """

    id_field = 'id'

    def __init__(
        self,
        related_url='', related_url_kwargs=None,
        self_url='', self_url_kwargs=None,
        include_data=False, many=False, type_=None, id_field=None, **kwargs
    ):
        self.related_url = related_url
        self.related_url_kwargs = related_url_kwargs or {}
        self.self_url = self_url
        self.self_url_kwargs = self_url_kwargs or {}
        if include_data and not type_:
            raise ValueError('include_data=True requires the type_ argument.')
        self.many = many
        self.include_data = include_data
        self.type_ = type_
        self.id_field = id_field or self.id_field
        super(Relationship, self).__init__(**kwargs)

    def get_related_url(self, obj):
        if self.related_url:
            kwargs = resolve_params(obj, self.related_url_kwargs)
            return self.related_url.format(**kwargs)
        return None

    def get_self_url(self, obj):
        if self.self_url:
            kwargs = resolve_params(obj, self.self_url_kwargs)
            return self.self_url.format(**kwargs)
        return None

    def add_resource_linkage(self, value):
        def stringify(value):
            if value is not None:
                return str(value)
            return value

        if self.many:
            included_data = [{
                'type': self.type_,
                'id': stringify(get_value(self.id_field, each, each))
            } for each in value]
        else:
            included_data = {
                'type': self.type_,
                'id': stringify(get_value(self.id_field, value, value))
            }
        return included_data

    def extract_value(self, data):
        """Extract the id key and validate the request structure."""
        errors = []
        if 'id' not in data:
            errors.append('Must have an `id` field')

        if 'type' not in data:
            errors.append('Must have a `type` field')
        elif data['type'] != self.type_:
            errors.append('Invalid `type` specified')

        if errors:
            raise ValidationError(errors)
        return data.get('id')

    def deserialize(self, value, attr=None, data=None):
        """Deserialize ``value``.

        :raise ValidationError: If the value is not type `dict`, if the
            value does not contain a `data` key, and if the value is
            required but unspecified.
        """
        if not isinstance(value, dict) or 'data' not in value:
            raise ValidationError('Must include a `data` key')
        return super(Relationship, self).deserialize(value['data'], attr, data)

    def _deserialize(self, value, attr, obj):
        if self.many:
            if not is_collection(value):
                raise ValidationError('Relationship is list-like')
            return [self.extract_value(item) for item in value]

        if is_collection(value):
            raise ValidationError('Relationship is not list-like')
        return self.extract_value(value)

    def _serialize(self, value, attr, obj):
        dict_class = self.parent.dict_class if self.parent else dict

        ret = dict_class()
        self_url = self.get_self_url(obj)
        related_url = self.get_related_url(obj)
        if self_url or related_url:
            ret['links'] = dict_class()
            if self_url:
                ret['links']['self'] = self_url
            if related_url:
                ret['links']['related'] = related_url

        if self.include_data:
            if value is None:
                ret['data'] = [] if self.many else None
            else:
                ret['data'] = self.add_resource_linkage(value)
        return ret
