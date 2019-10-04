import pytest

from hashlib import md5
from marshmallow import ValidationError, missing as missing_
from marshmallow.fields import Int

from marshmallow_jsonapi import Schema
from marshmallow_jsonapi.fields import Str, DocumentMeta, ResourceMeta, Relationship
from marshmallow_jsonapi.utils import _MARSHMALLOW_VERSION_INFO


class TestGenericRelationshipField:
    def test_serialize_relationship_link(self, post):
        field = Relationship(
            "http://example.com/posts/{id}/comments", related_url_kwargs={"id": "<id>"}
        )
        result = field.serialize("comments", post)
        assert field.serialize("comments", post)
        related = result["links"]["related"]
        assert related == f"http://example.com/posts/{post.id}/comments"

    def test_serialize_self_link(self, post):
        field = Relationship(
            self_url="http://example.com/posts/{id}/relationships/comments",
            self_url_kwargs={"id": "<id>"},
        )
        result = field.serialize("comments", post)
        related = result["links"]["self"]
        assert "related" not in result["links"]
        assert related == "http://example.com/posts/{id}/relationships/comments".format(
            id=post.id
        )

    def test_include_resource_linkage_requires_type(self):
        with pytest.raises(ValueError) as excinfo:
            Relationship(
                related_url="/posts/{post_id}",
                related_url_kwargs={"post_id": "<id>"},
                include_resource_linkage=True,
            )
        assert (
            excinfo.value.args[0]
            == "include_resource_linkage=True requires the type_ argument."
        )

    def test_include_resource_linkage_single(self, post):
        field = Relationship(
            related_url="/posts/{post_id}/author/",
            related_url_kwargs={"post_id": "<id>"},
            include_resource_linkage=True,
            type_="people",
        )
        result = field.serialize("author", post)
        assert "data" in result
        assert result["data"]
        assert result["data"]["id"] == str(post.author.id)

    def test_include_resource_linkage_single_with_schema(self, post):
        field = Relationship(
            related_url="/posts/{post_id}/author/",
            related_url_kwargs={"post_id": "<id>"},
            include_resource_linkage=True,
            type_="people",
            schema="PostSchema",
        )
        result = field.serialize("author", post)
        assert "data" in result
        assert result["data"]
        assert result["data"]["id"] == str(post.author.id)

    def test_include_resource_linkage_single_foreign_key(self, post):
        field = Relationship(
            related_url="/posts/{post_id}/author/",
            related_url_kwargs={"post_id": "<id>"},
            include_resource_linkage=True,
            type_="people",
        )
        result = field.serialize("author_id", post)
        assert result["data"]["id"] == str(post.author_id)

    def test_include_resource_linkage_single_foreign_key_with_schema(self, post):
        field = Relationship(
            related_url="/posts/{post_id}/author/",
            related_url_kwargs={"post_id": "<id>"},
            include_resource_linkage=True,
            type_="people",
            schema="PostSchema",
        )
        result = field.serialize("author_id", post)
        assert result["data"]["id"] == str(post.author_id)

    def test_include_resource_linkage_id_field_from_string(self):
        field = Relationship(
            include_resource_linkage=True, type_="authors", id_field="name"
        )
        result = field.serialize("author", {"author": {"name": "Ray Bradbury"}})
        assert "data" in result
        assert result["data"]
        assert result["data"]["id"] == "Ray Bradbury"

    def test_include_resource_linkage_id_field_from_schema(self):
        class AuthorSchema(Schema):
            id = Str(attribute="name")

            class Meta:
                type_ = "authors"
                strict = True

        field = Relationship(
            include_resource_linkage=True, type_="authors", schema=AuthorSchema
        )
        result = field.serialize("author", {"author": {"name": "Ray Bradbury"}})
        assert "data" in result
        assert result["data"]
        assert result["data"]["id"] == "Ray Bradbury"

    def test_include_resource_linkage_many(self, post):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            many=True,
            include_resource_linkage=True,
            type_="comments",
        )
        result = field.serialize("comments", post)
        assert "data" in result
        ids = [each["id"] for each in result["data"]]
        assert ids == [str(each.id) for each in post.comments]

    def test_include_resource_linkage_many_with_schema(self, post):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            many=True,
            include_resource_linkage=True,
            type_="comments",
            schema="CommentSchema",
        )
        result = field.serialize("comments", post)
        assert "data" in result
        ids = [each["id"] for each in result["data"]]
        assert ids == [str(each.id) for each in post.comments]

    def test_include_resource_linkage_many_with_schema_overriding_get_attribute(
        self, post
    ):
        field = Relationship(
            related_url="/posts/{post_id}/keywords",
            related_url_kwargs={"post_id": "<id>"},
            many=True,
            include_resource_linkage=True,
            type_="keywords",
            schema="KeywordSchema",
        )
        result = field.serialize("keywords", post)
        assert "data" in result
        ids = [each["id"] for each in result["data"]]
        assert ids == [
            md5(each.keyword.encode("utf-8")).hexdigest() for each in post.keywords
        ]

    def test_deserialize_data_single(self):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            many=False,
            include_resource_linkage=True,
            type_="comments",
        )
        value = {"data": {"type": "comments", "id": "1"}}
        result = field.deserialize(value)
        assert result == "1"

    def test_deserialize_data_many(self):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            many=True,
            include_resource_linkage=True,
            type_="comments",
        )
        value = {"data": [{"type": "comments", "id": "1"}]}
        result = field.deserialize(value)
        assert result == ["1"]

    def test_deserialize_data_missing_id(self):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            many=False,
            include_resource_linkage=True,
            type_="comments",
        )
        with pytest.raises(ValidationError) as excinfo:
            value = {"data": {"type": "comments"}}
            field.deserialize(value)
        assert excinfo.value.args[0] == ["Must have an `id` field"]

    def test_deserialize_data_missing_type(self):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            many=False,
            include_resource_linkage=True,
            type_="comments",
        )
        with pytest.raises(ValidationError) as excinfo:
            value = {"data": {"id": "1"}}
            field.deserialize(value)
        assert excinfo.value.args[0] == ["Must have a `type` field"]

    def test_deserialize_data_incorrect_type(self):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            many=False,
            include_resource_linkage=True,
            type_="comments",
        )
        with pytest.raises(ValidationError) as excinfo:
            value = {"data": {"type": "posts", "id": "1"}}
            field.deserialize(value)
        assert excinfo.value.args[0] == ["Invalid `type` specified"]

    def test_deserialize_null_data_value(self):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            allow_none=True,
            many=False,
            include_resource_linkage=False,
            type_="comments",
        )
        result = field.deserialize({"data": None})
        assert result is None

    def test_deserialize_null_value_disallow_none(self):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            allow_none=False,
            many=False,
            include_resource_linkage=False,
            type_="comments",
        )
        with pytest.raises(ValidationError) as excinfo:
            field.deserialize({"data": None})
        assert excinfo.value.args[0] == "Field may not be null."

    def test_deserialize_empty_data_list(self):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            many=True,
            include_resource_linkage=False,
            type_="comments",
        )
        result = field.deserialize({"data": []})
        assert result == []

    def test_deserialize_empty_data(self):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            many=False,
            include_resource_linkage=False,
            type_="comments",
        )
        with pytest.raises(ValidationError) as excinfo:
            field.deserialize({"data": {}})
        assert excinfo.value.args[0] == [
            "Must have an `id` field",
            "Must have a `type` field",
        ]

    def test_deserialize_required_missing(self):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            required=True,
            many=False,
            include_resource_linkage=True,
            type_="comments",
        )
        with pytest.raises(ValidationError) as excinfo:
            field.deserialize(missing_)
        assert excinfo.value.args[0] == "Missing data for required field."

    def test_deserialize_required_empty(self):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            required=True,
            many=False,
            include_resource_linkage=False,
            type_="comments",
        )
        with pytest.raises(ValidationError) as excinfo:
            field.deserialize({})
        assert excinfo.value.args[0] == "Must include a `data` key"

    @pytest.mark.skipif(
        _MARSHMALLOW_VERSION_INFO[0] < 3,
        reason="deserialize does not handle missing skeleton",
    )
    def test_deserialize_missing(self):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            many=False,
            include_resource_linkage=True,
            type_="comments",
        )
        result = field.deserialize(missing_)
        assert result is missing_

    @pytest.mark.skipif(
        _MARSHMALLOW_VERSION_INFO[0] < 3,
        reason="deserialize does not handle missing skeleton",
    )
    def test_deserialize_missing_with_missing_param(self):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            missing="value",
            many=False,
            include_resource_linkage=True,
            type_="comments",
        )
        result = field.deserialize(missing_)
        assert result == "value"

    def test_deserialize_many_non_list_relationship(self):
        field = Relationship(many=True, include_resource_linkage=True, type_="comments")
        with pytest.raises(ValidationError) as excinfo:
            field.deserialize({"data": "1"})
        assert excinfo.value.args[0] == "Relationship is list-like"

    def test_deserialize_non_many_list_relationship(self):
        field = Relationship(
            many=False, include_resource_linkage=True, type_="comments"
        )
        with pytest.raises(ValidationError) as excinfo:
            field.deserialize({"data": ["1"]})
        assert excinfo.value.args[0] == "Relationship is not list-like"

    def test_include_null_data_single(self, post_with_null_author):
        field = Relationship(
            related_url="posts/{post_id}/author",
            related_url_kwargs={"post_id": "<id>"},
            include_resource_linkage=True,
            type_="people",
        )
        result = field.serialize("author", post_with_null_author)
        assert result and result["links"]["related"]
        assert result["data"] is None

    def test_include_null_data_many(self, post_with_null_comment):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            many=True,
            include_resource_linkage=True,
            type_="comments",
        )
        result = field.serialize("comments", post_with_null_comment)
        assert result and result["links"]["related"]
        assert result["data"] == []

    def test_exclude_data(self, post_with_null_comment):
        field = Relationship(
            related_url="/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            many=True,
            include_resource_linkage=False,
            type_="comments",
        )
        result = field.serialize("comments", post_with_null_comment)
        assert result and result["links"]["related"]
        assert "data" not in result

    def test_empty_relationship_with_alternative_identifier_field(
        self, post_with_null_author
    ):
        field = Relationship(
            related_url="/authors/{author_id}",
            related_url_kwargs={"author_id": "<author.last_name>"},
            default=None,
        )
        result = field.serialize("author", post_with_null_author)

        assert not result

    def test_resource_linkage_id_type_from_schema(self):
        class AuthorSchema(Schema):
            id = Int(attribute="author_id", as_string=True)

            class Meta:
                type_ = "authors"
                strict = True

        field = Relationship(
            include_resource_linkage=True, type_="authors", schema=AuthorSchema
        )

        result = field.deserialize({"data": {"type": "authors", "id": "1"}})

        assert result == 1

    def test_resource_linkage_id_of_invalid_type(self):
        class AuthorSchema(Schema):
            id = Int(attribute="author_id", as_string=True)

            class Meta:
                type_ = "authors"
                strict = True

        field = Relationship(
            include_resource_linkage=True, type_="authors", schema=AuthorSchema
        )

        with pytest.raises(ValidationError) as excinfo:
            field.deserialize({"data": {"type": "authors", "id": "not_a_number"}})
        assert excinfo.value.args[0] == "Not a valid integer."


class TestDocumentMetaField:
    def test_serialize(self):
        field = DocumentMeta()
        result = field.serialize(
            "document_meta", {"document_meta": {"page": {"offset": 1}}}
        )
        assert result == {"page": {"offset": 1}}

    def test_serialize_incorrect_type(self):
        field = DocumentMeta()
        with pytest.raises(ValidationError) as excinfo:
            field.serialize("document_meta", {"document_meta": 1})
        assert excinfo.value.args[0] == "Not a valid mapping type."

    def test_deserialize(self):
        field = DocumentMeta()
        value = {"page": {"offset": 1}}
        result = field.deserialize(value)
        assert result == value

    def test_deserialize_incorrect_type(self):
        field = DocumentMeta()
        value = 1
        with pytest.raises(ValidationError) as excinfo:
            field.deserialize(value)
        assert excinfo.value.args[0] == "Not a valid mapping type."


class TestResourceMetaField:
    def test_serialize(self):
        field = ResourceMeta()
        result = field.serialize("resource_meta", {"resource_meta": {"active": True}})
        assert result == {"active": True}

    def test_serialize_incorrect_type(self):
        field = ResourceMeta()
        with pytest.raises(ValidationError) as excinfo:
            field.serialize("resource_meta", {"resource_meta": True})
        assert excinfo.value.args[0] == "Not a valid mapping type."

    def test_deserialize(self):
        field = ResourceMeta()
        value = {"active": True}
        result = field.deserialize(value)
        assert result == value

    def test_deserialize_incorrect_type(self):
        field = ResourceMeta()
        value = True
        with pytest.raises(ValidationError) as excinfo:
            field.deserialize(value)
        assert excinfo.value.args[0] == "Not a valid mapping type."
