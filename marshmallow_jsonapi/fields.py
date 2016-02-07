# -*- coding: utf-8 -*-
"""Includes all the fields classes from `marshmallow.fields` as well as
fields for serializing JSON API-formatted hyperlinks.
"""
from marshmallow import ValidationError
# Make core fields importable from marshmallow_jsonapi
from marshmallow.fields import *  # noqa
from marshmallow.utils import get_value

from .utils import resolve_params


class BaseRelationship(Field):
    """Base relationship field. This is used by `marshmallow_jsonapi.Schema` to determine
    which fields should be formatted as relationship objects.

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

    def validate_data_object(self, data):
        errors = []
        if 'id' not in data:
            errors.append('Must have an `id` field')
        if 'type' not in data:
            errors.append('Must have a `type` field')
        elif data['type'] != self.type_:
            errors.append('Invalid `type` specified')

        if errors:
            raise ValidationError(errors)

    def _deserialize(self, value, attr, obj):
        if 'data' not in value:
            raise ValidationError('Must include a `data` key')

        data = value.get('data')
        if data is None or value['data'] == []:
            return data

        if self.many:
            for item in data:
                self.validate_data_object(item)
        else:
            self.validate_data_object(data)

        if self.many:
            return [item.get('id') for item in data]
        return data.get('id')

    def _serialize(self, value, attr, obj):
        dict_class = self.parent.dict_class if self.parent else dict
        ret = dict_class()
        if hasattr(self.root, 'inflect'):
            attr = self.root.inflect(attr)
        ret[attr] = dict_class()

        self_url = self.get_self_url(obj)
        related_url = self.get_related_url(obj)
        if self_url or related_url:
            ret[attr]['links'] = dict_class()
            if self_url:
                ret[attr]['links']['self'] = self_url
            if related_url:
                ret[attr]['links']['related'] = related_url

        if self.include_data:
            if value is None:
                ret[attr]['data'] = [] if self.many else None
            else:
                ret[attr]['data'] = self.add_resource_linkage(value)
        return ret
