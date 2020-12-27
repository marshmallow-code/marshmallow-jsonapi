import itertools

import marshmallow as ma
from marshmallow.exceptions import ValidationError
from marshmallow.utils import is_collection

from .fields import BaseRelationship, DocumentMeta, ResourceMeta
from .fields import _RESOURCE_META_LOAD_FROM, _DOCUMENT_META_LOAD_FROM
from .exceptions import IncorrectTypeError
from .utils import resolve_params

TYPE = "type"
ID = "id"


class SchemaOpts(ma.SchemaOpts):
    def __init__(self, meta, *args, **kwargs):
        super().__init__(meta, *args, **kwargs)
        self.type_ = getattr(meta, "type_", None)
        self.inflect = getattr(meta, "inflect", None)
        self.self_url = getattr(meta, "self_url", None)
        self.self_url_kwargs = getattr(meta, "self_url_kwargs", None)
        self.self_url_many = getattr(meta, "self_url_many", None)


class Schema(ma.Schema):
    """Schema class that formats data according to JSON API 1.0.
    Must define the ``type_`` `class Meta` option.

    Example: ::

        from marshmallow_jsonapi import Schema, fields

        def dasherize(text):
            return text.replace('_', '-')

        class PostSchema(Schema):
            id = fields.Str(dump_only=True)  # Required
            title = fields.Str()

            author = fields.HyperlinkRelated(
                '/authors/{author_id}',
                url_kwargs={'author_id': '<author.id>'},
            )

            comments = fields.HyperlinkRelated(
                '/posts/{post_id}/comments',
                url_kwargs={'post_id': '<id>'},
                # Include resource linkage
                many=True, include_resource_linkage=True,
                type_='comments'
            )

            class Meta:
                type_ = 'posts'  # Required
                inflect = dasherize

    """

    class Meta:
        """Options object for `Schema`. Takes the same options as `marshmallow.Schema.Meta` with
        the addition of:

        * ``type_`` - required, the JSON API resource type as a string.
        * ``inflect`` - optional, an inflection function to modify attribute names.
        * ``self_url`` - optional, URL to use to `self` in links
        * ``self_url_kwargs`` - optional, replacement fields for `self_url`.
          String arguments enclosed in ``< >`` will be interpreted as attributes
          to pull from the schema data.
        * ``self_url_many`` - optional, URL to use to `self` in top-level ``links``
          when a collection of resources is returned.
        """

        pass

    def __init__(self, *args, **kwargs):
        self.include_data = kwargs.pop("include_data", ())
        super().__init__(*args, **kwargs)
        if self.include_data:
            self.check_relations(self.include_data)

        if not self.opts.type_:
            raise ValueError("Must specify type_ class Meta option")

        if "id" not in self.fields:
            raise ValueError("Must have an `id` field")

        if self.opts.self_url_kwargs and not self.opts.self_url:
            raise ValueError(
                "Must specify `self_url` Meta option when "
                "`self_url_kwargs` is specified"
            )
        self.included_data = {}
        self.document_meta = {}

    OPTIONS_CLASS = SchemaOpts

    def check_relations(self, relations):
        """Recursive function which checks if a relation is valid."""
        for rel in relations:
            if not rel:
                continue
            fields = rel.split(".", 1)

            local_field = fields[0]
            if local_field not in self.fields:
                raise ValueError(f'Unknown field "{local_field}"')

            field = self.fields[local_field]
            if not isinstance(field, BaseRelationship):
                raise ValueError(
                    'Can only include relationships. "{}" is a "{}"'.format(
                        field.name, field.__class__.__name__
                    )
                )

            field.include_data = True
            if len(fields) > 1:
                field.schema.check_relations(fields[1:])

    @ma.post_dump(pass_many=True)
    def format_json_api_response(self, data, many, **kwargs):
        """Post-dump hook that formats serialized data as a top-level JSON API object.

        See: http://jsonapi.org/format/#document-top-level
        """
        ret = self.format_items(data, many)
        ret = self.wrap_response(ret, many)
        ret = self.render_included_data(ret)
        ret = self.render_meta_document(ret)
        return ret

    def render_included_data(self, data):
        if not self.included_data:
            return data
        data["included"] = list(self.included_data.values())
        return data

    def render_meta_document(self, data):
        if not self.document_meta:
            return data
        data["meta"] = self.document_meta
        return data

    def unwrap_item(self, item):
        if "type" not in item:
            raise ma.ValidationError(
                [
                    {
                        "detail": "`data` object must include `type` key.",
                        "source": {"pointer": "/data"},
                    }
                ]
            )
        if item["type"] != self.opts.type_:
            raise IncorrectTypeError(actual=item["type"], expected=self.opts.type_)

        payload = self.dict_class()
        if "id" in item:
            payload["id"] = item["id"]
        if "meta" in item:
            payload[_RESOURCE_META_LOAD_FROM] = item["meta"]
        if self.document_meta:
            payload[_DOCUMENT_META_LOAD_FROM] = self.document_meta
        for key, value in item.get("attributes", {}).items():
            payload[key] = value
        for key, value in item.get("relationships", {}).items():
            # Fold included data related to this relationship into the item, so
            # that we can deserialize the whole objects instead of just IDs.
            if self.included_data:
                included_data = []
                inner_data = value.get("data", [])

                # Data may be ``None`` (for empty relationships), but we only
                # need to process it when it's present.
                if inner_data:
                    if not is_collection(inner_data):
                        included_data = next(
                            self._extract_from_included(inner_data), None
                        )
                    else:
                        for data in inner_data:
                            included_data.extend(self._extract_from_included(data))

                if included_data:
                    value["data"] = included_data

            payload[key] = value
        return payload

    @ma.pre_load(pass_many=True)
    def unwrap_request(self, data, many, **kwargs):
        if "data" not in data:
            raise ma.ValidationError(
                [
                    {
                        "detail": "Object must include `data` key.",
                        "source": {"pointer": "/"},
                    }
                ]
            )

        data = data["data"]
        if many:
            if not is_collection(data):
                raise ma.ValidationError(
                    [
                        {
                            "detail": "`data` expected to be a collection.",
                            "source": {"pointer": "/data"},
                        }
                    ]
                )
            return [self.unwrap_item(each) for each in data]
        return self.unwrap_item(data)

    def on_bind_field(self, field_name, field_obj):
        """Schema hook override. When binding fields, set ``data_key`` to the inflected form of field_name."""
        if not field_obj.data_key:
            field_obj.data_key = self.inflect(field_name)
        return None

    def _do_load(self, data, many=None, **kwargs):
        """Override `marshmallow.Schema._do_load` for custom JSON API handling.

        Specifically, we do this to format errors as JSON API Error objects,
        and to support loading of included data.
        """
        many = self.many if many is None else bool(many)

        # Store this on the instance so we have access to the included data
        # when processing relationships (``included`` is outside of the
        # ``data``).
        self.included_data = data.get("included", {})
        self.document_meta = data.get("meta", {})

        try:
            result = super()._do_load(data, many=many, **kwargs)
        except ValidationError as err:  # strict mode
            error_messages = err.messages
            if "_schema" in error_messages:
                error_messages = error_messages["_schema"]
            formatted_messages = self.format_errors(error_messages, many=many)
            err.messages = formatted_messages
            raise err
        return result

    def _extract_from_included(self, data):
        """Extract included data matching the items in ``data``.

        For each item in ``data``, extract the full data from the included
        data.
        """
        return (
            item
            for item in self.included_data
            if item["type"] == data["type"] and str(item["id"]) == str(data["id"])
        )

    def inflect(self, text):
        """Inflect ``text`` if the ``inflect`` class Meta option is defined, otherwise
        do nothing.
        """
        return self.opts.inflect(text) if self.opts.inflect else text

    ### Overridable hooks ###

    def format_errors(self, errors, many):
        """Format validation errors as JSON Error objects."""
        if not errors:
            return {}
        if isinstance(errors, (list, tuple)):
            return {"errors": errors}

        formatted_errors = []
        if many:
            for index, i_errors in errors.items():
                formatted_errors.extend(self._get_formatted_errors(i_errors, index))
        else:
            formatted_errors.extend(self._get_formatted_errors(errors))

        return {"errors": formatted_errors}

    def _get_formatted_errors(self, errors, index=None):
        return itertools.chain(
            *(
                [
                    self.format_error(field_name, message, index=index)
                    for message in field_errors
                ]
                for field_name, field_errors in itertools.chain(
                    *(self._process_nested_errors(k, v) for k, v in errors.items())
                )
            )
        )

    def _process_nested_errors(self, name, data):
        if not isinstance(data, dict):
            return [(name, data)]

        return itertools.chain(
            *(self._process_nested_errors(f"{name}/{k}", v) for k, v in data.items())
        )

    def format_error(self, field_name, message, index=None):
        """Override-able hook to format a single error message as an Error object.

        See: http://jsonapi.org/format/#error-objects
        """
        pointer = ["/data"]

        if index is not None:
            pointer.append(str(index))

        relationship = isinstance(
            self.declared_fields.get(field_name), BaseRelationship
        )
        if relationship:
            pointer.append("relationships")
        elif field_name != "id":
            # JSONAPI identifier is a special field that exists above the attribute object.
            pointer.append("attributes")

        pointer.append(self.inflect(field_name))

        if relationship:
            pointer.append("data")

        return {"detail": message, "source": {"pointer": "/".join(pointer)}}

    def format_item(self, item):
        """Format a single datum as a Resource object.

        See: http://jsonapi.org/format/#document-resource-objects
        """
        # http://jsonapi.org/format/#document-top-level
        # Primary data MUST be either... a single resource object, a single resource
        # identifier object, or null, for requests that target single resources
        if not item:
            return None

        ret = self.dict_class()
        ret[TYPE] = self.opts.type_

        # Get the schema attributes so we can confirm `dump-to` values exist
        attributes = {
            (self.fields[field].data_key or field): field for field in self.fields
        }

        for field_name, value in item.items():
            attribute = attributes[field_name]
            if attribute == ID:
                ret[ID] = value
            elif isinstance(self.fields[attribute], DocumentMeta):
                if not self.document_meta:
                    self.document_meta = self.dict_class()
                self.document_meta.update(value)
            elif isinstance(self.fields[attribute], ResourceMeta):
                if "meta" not in ret:
                    ret["meta"] = self.dict_class()
                ret["meta"].update(value)
            elif isinstance(self.fields[attribute], BaseRelationship):
                if value:
                    if "relationships" not in ret:
                        ret["relationships"] = self.dict_class()
                    ret["relationships"][self.inflect(field_name)] = value
            else:
                if "attributes" not in ret:
                    ret["attributes"] = self.dict_class()
                ret["attributes"][self.inflect(field_name)] = value

        links = self.get_resource_links(item)
        if links:
            ret["links"] = links
        return ret

    def format_items(self, data, many):
        """Format data as a Resource object or list of Resource objects.

        See: http://jsonapi.org/format/#document-resource-objects
        """
        if many:
            return [self.format_item(item) for item in data]
        else:
            return self.format_item(data)

    def get_top_level_links(self, data, many):
        """Hook for adding links to the root of the response data."""
        self_link = None

        if many:
            if self.opts.self_url_many:
                self_link = self.generate_url(self.opts.self_url_many)
        else:
            if self.opts.self_url:
                self_link = data.get("links", {}).get("self", None)

        return {"self": self_link}

    def get_resource_links(self, item):
        """Hook for adding links to a resource object."""
        if self.opts.self_url:
            ret = self.dict_class()
            kwargs = resolve_params(item, self.opts.self_url_kwargs or {})
            ret["self"] = self.generate_url(self.opts.self_url, **kwargs)
            return ret
        return None

    def wrap_response(self, data, many):
        """Wrap data and links according to the JSON API """
        ret = {"data": data}
        # self_url_many is still valid when there isn't any data, but self_url
        # may only be included if there is data in the ret
        if many or data:
            top_level_links = self.get_top_level_links(data, many)
            if top_level_links["self"]:
                ret["links"] = top_level_links
        return ret

    def generate_url(self, link, **kwargs):
        """Generate URL with any kwargs interpolated."""
        return link.format_map(kwargs) if link else None
