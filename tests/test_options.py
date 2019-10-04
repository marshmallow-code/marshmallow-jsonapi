import pytest
from marshmallow import validate, ValidationError

from marshmallow_jsonapi import Schema, fields
from tests.base import unpack, AuthorSchema, CommentSchema
from tests.test_schema import make_serialized_author, get_error_by_field


def dasherize(text):
    return text.replace("_", "-")


class AuthorSchemaWithInflection(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=2))
    last_name = fields.Str(required=True)

    class Meta:
        type_ = "people"
        inflect = dasherize
        strict = True


class AuthorSchemaWithOverrideInflection(Schema):
    id = fields.Str(dump_only=True)
    # data_key and load_from takes precedence over inflected attribute
    first_name = fields.Str(data_key="firstName", load_from="firstName")
    last_name = fields.Str()

    class Meta:
        type_ = "people"
        inflect = dasherize
        strict = True


class TestInflection:
    @pytest.fixture()
    def schema(self):
        return AuthorSchemaWithInflection()

    def test_dump(self, schema, author):
        data = unpack(schema.dump(author))

        assert data["data"]["id"] == author.id
        assert data["data"]["type"] == "people"
        attribs = data["data"]["attributes"]

        assert "first-name" in attribs
        assert "last-name" in attribs

        assert attribs["first-name"] == author.first_name
        assert attribs["last-name"] == author.last_name

    def test_validate_with_inflection(self, schema):
        try:
            errors = schema.validate(make_serialized_author({"first-name": "d"}))
        except ValidationError as err:  # marshmallow 2
            errors = err.messages
        lname_err = get_error_by_field(errors, "last-name")
        assert lname_err
        assert lname_err["detail"] == "Missing data for required field."

        fname_err = get_error_by_field(errors, "first-name")
        assert fname_err
        assert fname_err["detail"] == "Shorter than minimum length 2."

    def test_load_with_inflection(self, schema):
        # invalid
        with pytest.raises(ValidationError) as excinfo:
            schema.load(make_serialized_author({"first-name": "d"}))
        errors = excinfo.value.messages
        fname_err = get_error_by_field(errors, "first-name")
        assert fname_err
        assert fname_err["detail"] == "Shorter than minimum length 2."

        # valid
        data = unpack(
            schema.load(
                make_serialized_author(
                    {"first-name": "Nevets", "last-name": "Longoria"}
                )
            )
        )
        assert data["first_name"] == "Nevets"

    def test_load_with_inflection_and_load_from_override(self):
        schema = AuthorSchemaWithOverrideInflection()
        data = unpack(
            schema.load(
                make_serialized_author({"firstName": "Steve", "last-name": "Loria"})
            )
        )
        assert data["first_name"] == "Steve"
        assert data["last_name"] == "Loria"

    def test_load_bulk_id_fields(self):
        request = {"data": [{"id": "1", "type": "people"}]}

        result = unpack(AuthorSchema(only=("id",), many=True).load(request))
        assert type(result) is list

        response = result[0]
        assert response["id"] == request["data"][0]["id"]

    def test_relationship_keys_get_inflected(self, post):
        class PostSchema(Schema):
            id = fields.Int()
            post_title = fields.Str(attribute="title")

            post_comments = fields.Relationship(
                "http://test.test/posts/{id}/comments/",
                related_url_kwargs={"id": "<id>"},
                attribute="comments",
            )

            class Meta:
                type_ = "posts"
                inflect = dasherize
                strict = True

        data = unpack(PostSchema().dump(post))
        assert "post-title" in data["data"]["attributes"]
        assert "post-comments" in data["data"]["relationships"]
        related_href = data["data"]["relationships"]["post-comments"]["links"][
            "related"
        ]
        assert related_href == f"http://test.test/posts/{post.id}/comments/"


class AuthorAutoSelfLinkSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    password = fields.Str(load_only=True, validate=validate.Length(6))
    twitter = fields.Str()

    class Meta:
        type_ = "people"
        self_url = "/authors/{id}"
        self_url_kwargs = {"id": "<id>"}
        self_url_many = "/authors/"


class AuthorAutoSelfLinkFirstLastSchema(AuthorAutoSelfLinkSchema):
    class Meta:
        type_ = "people"
        self_url = "http://example.com/authors/{first_name} {last_name}"
        self_url_kwargs = {"first_name": "<first_name>", "last_name": "<last_name>"}
        self_url_many = "http://example.com/authors/"


class TestAutoSelfUrls:
    def test_self_url_kwargs_requires_self_url(self, author):
        class InvalidSelfLinkSchema(Schema):
            id = fields.Int()

            class Meta:
                type_ = "people"
                self_url_kwargs = {"id": "<id>"}

        with pytest.raises(ValueError):
            InvalidSelfLinkSchema().dump(author)

    def test_self_link_single(self, author):
        data = unpack(AuthorAutoSelfLinkSchema().dump(author))
        assert "links" in data
        assert data["links"]["self"] == f"/authors/{author.id}"

    def test_self_link_many(self, authors):
        data = unpack(AuthorAutoSelfLinkSchema(many=True).dump(authors))
        assert "links" in data
        assert data["links"]["self"] == "/authors/"

        assert "links" in data["data"][0]
        assert data["data"][0]["links"]["self"] == "/authors/{}".format(authors[0].id)

    def test_without_self_link(self, comments):
        data = unpack(CommentSchema(many=True).dump(comments))

        assert "data" in data
        assert type(data["data"]) is list

        first = data["data"][0]
        assert first["id"] == str(comments[0].id)
        assert first["type"] == "comments"

        assert "links" not in data
