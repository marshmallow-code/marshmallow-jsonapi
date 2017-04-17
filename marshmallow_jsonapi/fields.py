# -*- coding: utf-8 -*-
"""Includes all the fields classes from `marshmallow.fields` as well as
fields for serializing JSON API-formatted hyperlinks.
"""
import collections

from marshmallow.compat import basestring

from marshmallow import ValidationError, class_registry
# Make core fields importable from marshmallow_jsonapi
from marshmallow.fields import *  # noqa
from marshmallow.base import SchemaABC
from marshmallow.utils import is_collection

from .utils import get_value, resolve_params, iteritems


_RECURSIVE_NESTED = 'self'
# JSON API disallows U+005F LOW LINE at the start of amember name, so we can use
# it to load the Meta type from since it can't clash with an attribute named
# meta (which isn't disallowed by the spec).
_META_LOAD_FROM = '_meta'


class BaseRelationship(Field):
    """Base relationship field.

    This is used by `marshmallow_jsonapi.Schema` to determine which
    fields should be formatted as relationship objects.

    See: http://jsonapi.org/format/#document-resource-object-relationships
    """

    pass


def _stringify(value):
    if value is not None:
        return str(value)
    return value


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
            many=True, include_resource_linkage=True,
            type_='comments'
        )

    This field is read-only by default.

    :param str related_url: Format string for related resource links.
    :param dict related_url_kwargs: Replacement fields for `related_url`. String arguments
        enclosed in `< >` will be interpreted as attributes to pull from the target object.
    :param str self_url: Format string for self relationship links.
    :param dict self_url_kwargs: Replacement fields for `self_url`. String arguments
        enclosed in `< >` will be interpreted as attributes to pull from the target object.
    :param bool include_resource_linkage: Whether to include a resource linkage
        (http://jsonapi.org/format/#document-resource-object-linkage) in the serialized result.
    :param Schema schema: The schema to render the included data with.
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
        include_resource_linkage=False, schema=None,
        many=False, type_=None, id_field=None, **kwargs
    ):
        self.related_url = related_url
        self.related_url_kwargs = related_url_kwargs or {}
        self.self_url = self_url
        self.self_url_kwargs = self_url_kwargs or {}
        if include_resource_linkage and not type_:
            raise ValueError('include_resource_linkage=True requires the type_ argument.')
        self.many = many
        self.include_resource_linkage = include_resource_linkage
        self.include_data = False
        self.__schema = schema
        self.type_ = type_
        self.id_field = id_field or self.id_field
        super(Relationship, self).__init__(**kwargs)

    @property
    def schema(self):
        if isinstance(self.__schema, SchemaABC):
            return self.__schema
        if isinstance(self.__schema, type) and issubclass(self.__schema, SchemaABC):
            self.__schema = self.__schema()
            return self.__schema
        if isinstance(self.__schema, basestring):
            if self.__schema == _RECURSIVE_NESTED:
                parent_class = self.parent.__class__
                self.__schema = parent_class(include_data=self.parent.include_data)
            else:
                schema_class = class_registry.get_class(self.__schema)
                self.__schema = schema_class()
            return self.__schema
        else:
            raise ValueError(('A Schema is required to serialize a nested '
                              'relationship with include_data'))

    def get_related_url(self, obj):
        if self.related_url:
            params = resolve_params(obj, self.related_url_kwargs, default=self.default)
            non_null_params = {
                key: value for key, value in params.items()
                if value is not None
            }
            if non_null_params:
                return self.related_url.format(**non_null_params)
        return None

    def get_self_url(self, obj):
        if self.self_url:
            params = resolve_params(obj, self.self_url_kwargs, default=self.default)
            non_null_params = {
                key: value for key, value in params.items()
                if value is not None
            }
            if non_null_params:
                return self.self_url.format(**non_null_params)
        return None

    def get_resource_linkage(self, value):
        if self.many:
            resource_object = [{
                'type': self.type_,
                'id': _stringify(get_value(each, self.id_field, each))
            } for each in value]
        else:
            resource_object = {
                'type': self.type_,
                'id': _stringify(get_value(value, self.id_field, value))
            }
        return resource_object

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

        # resource linkage is required when including the data
        if self.include_resource_linkage or self.include_data:
            if value is None:
                ret['data'] = [] if self.many else None
            else:
                ret['data'] = self.get_resource_linkage(value)

        if self.include_data and value is not None:
            if self.many:
                for item in value:
                    self._serialize_included(item)
            else:
                self._serialize_included(value)
        return ret

    def _serialize_included(self, value):
        result = self.schema.dump(value)
        if result.errors:
            raise ValidationError(result.errors)
        item = result.data['data']
        self.root.included_data[(item['type'], item['id'])] = item
        for key, value in iteritems(self.schema.included_data):
            self.root.included_data[key] = value


class Meta(Field):
    """Field which serializes to a "meta object" within  a "resource object".

    Examples: ::

        from marshmallow_jsonapi import Schema, fields

        class UserSchema(Schema):
            id = fields.String()
            metadata = fields.Meta()

            class Meta:
                type_ = 'product'
                strict = True

    See: http://jsonapi.org/format/#document-meta
    """

    default_error_messages = {
        'invalid': 'Not a valid mapping type.'
    }

    def __init__(self, **kwargs):
        super(Meta, self).__init__(**kwargs)
        self.load_from = _META_LOAD_FROM

    def _deserialize(self, value, attr, data):
        if isinstance(value, collections.Mapping):
            return value
        else:
            self.fail('invalid')

    def _serialize(self, value, *args, **kwargs):
        if isinstance(value, collections.Mapping):
            return super(Meta, self)._serialize(value, *args, **kwargs)
        else:
            self.fail('invalid')
