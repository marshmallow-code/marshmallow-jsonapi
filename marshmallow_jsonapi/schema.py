# -*- coding: utf-8 -*-
import marshmallow as ma
from marshmallow.compat import iteritems

from .fields import BaseHyperlink

TYPE = 'type'
ID = 'id'

class SchemaOpts(ma.SchemaOpts):

    def __init__(self, meta):
        super(SchemaOpts, self).__init__(meta)
        self.type_ = getattr(meta, 'type_', None)

class Schema(ma.Schema):
    """Schema class that formats data according to JSON API 1.0.
    Must define the ``type_`` `class Meta` option.

    Example: ::

        from marshmallow import validate
        from marshmallow_jsonapi import Schema, fields

        class AuthorSchema(Schema):
            id = fields.Str(dump_only=True)
            first_name = fields.Str(required=True)
            last_name = fields.Str(required=True)
            password = fields.Str(load_only=True, validate=validate.Length(6))
            twitter = fields.Str()

            class Meta:
                type_ = 'people'

    """
    OPTIONS_CLASS = SchemaOpts

    @ma.post_dump(raw=True)
    def format_json_api_response(self, data, many):
        ret = self.format_items(data, many)
        ret = self.wrap_response(ret, many)
        return ret

    # overrides ma.Schema._do_load so that we can format errors as JSON API Error objects.
    def _do_load(self, *args, **kwargs):
        data, errors = super(Schema, self)._do_load(*args, **kwargs)
        return data, self.format_errors(errors)

    ### Overridable hooks ###

    def format_errors(self, errors):
        """Format validation errors as JSON Error objects."""
        if not errors:
            return {}
        formatted_errors = []
        for field_name, field_errors in iteritems(errors):
            formatted_errors.extend([
                self.format_error(field_name, message)
                for message in field_errors
            ])
        return {'errors': formatted_errors}

    def format_error(self, field_name, message):
        """Override-able hook to format a single error message as an Error object.

        See: http://jsonapi.org/format/#error-objects
        """
        return {
            'detail': message,
            'source': {
                'pointer': '/data/attributes/{field_name}'.format(field_name=field_name)
            }
        }

    def format_item(self, item):
        """Format a single datum as a Resource object.

        See: http://jsonapi.org/format/#document-resource-objects
        """
        ret = self.dict_class()
        type_ = self.opts.type_
        ret[TYPE] = type_
        for field_name, value in iteritems(item):
            if field_name == ID:
                ret[ID] = value
            elif isinstance(self.fields[field_name], BaseHyperlink):
                if 'relationships' not in ret:
                    ret['relationships'] = self.dict_class()
                ret['relationships'].update(value)
            else:
                if 'attributes' not in ret:
                    ret['attributes'] = self.dict_class()
                ret['attributes'][field_name] = value
        return ret

    def format_items(self, data, many):
        """Format data as a Resource object or list of Resource objects."""
        if many:
            return [self.format_item(item) for item in data]
        else:
            return self.format_item(data)

    def get_top_level_links(self, data, many):
        """Hook for adding links to the root of the response data."""
        return None

    def wrap_response(self, data, many):
        """Wrap data and links according to the JSON API """
        ret = {'data': data}
        top_level_links = self.get_top_level_links(data, many)
        if top_level_links:
            ret['links'] = top_level_links
        return ret
