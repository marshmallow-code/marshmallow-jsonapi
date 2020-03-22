import pytest
import marshmallow as ma
from marshmallow import ValidationError

from marshmallow_jsonapi import Schema, fields
from marshmallow_jsonapi.exceptions import IncorrectTypeError
from marshmallow_jsonapi.utils import _MARSHMALLOW_VERSION_INFO
from tests.base import unpack
from tests.base import (
    AuthorSchema,
    CommentSchema,
    PostSchema,
    PolygonSchema,
    ArticleSchema,
)


def make_serialized_author(attributes):
    return {"data": {"type": "people", "attributes": attributes}}


def make_serialized_authors(items):
    return {"data": [{"type": "people", "attributes": each} for each in items]}


def test_type_is_required():
    class BadSchema(Schema):
        id = fields.Str()

        class Meta:
            pass

    with pytest.raises(ValueError) as excinfo:
        BadSchema()
    assert excinfo.value.args[0] == "Must specify type_ class Meta option"


def test_id_field_is_required():
    class BadSchema(Schema):
        class Meta:
            type_ = "users"

    with pytest.raises(ValueError) as excinfo:
        BadSchema()
    assert excinfo.value.args[0] == "Must have an `id` field"


class TestResponseFormatting:
    def test_dump_single(self, author):
        data = unpack(AuthorSchema().dump(author))

        assert "data" in data
        assert type(data["data"]) is dict

        assert data["data"]["id"] == str(author.id)
        assert data["data"]["type"] == "people"
        attribs = data["data"]["attributes"]

        assert attribs["first_name"] == author.first_name
        assert attribs["last_name"] == author.last_name

    def test_dump_many(self, authors):
        data = unpack(AuthorSchema(many=True).dump(authors))
        assert "data" in data
        assert type(data["data"]) is list

        first = data["data"][0]
        assert first["id"] == str(authors[0].id)
        assert first["type"] == "people"

        attribs = first["attributes"]

        assert attribs["first_name"] == authors[0].first_name
        assert attribs["last_name"] == authors[0].last_name

    def test_self_link_single(self, author):
        data = unpack(AuthorSchema().dump(author))
        assert "links" in data
        assert data["links"]["self"] == f"/authors/{author.id}"

    def test_self_link_many(self, authors):
        data = unpack(AuthorSchema(many=True).dump(authors))
        assert "links" in data
        assert data["links"]["self"] == "/authors/"

    def test_dump_to(self, post):
        data = unpack(PostSchema().dump(post))
        assert "data" in data
        assert "attributes" in data["data"]
        assert "title" in data["data"]["attributes"]
        assert "relationships" in data["data"]
        assert "post-comments" in data["data"]["relationships"]

    def test_dump_none(self):
        data = unpack(AuthorSchema().dump(None))

        assert "data" in data
        assert data["data"] is None
        assert "links" not in data

    def test_dump_empty_list(self):
        data = unpack(AuthorSchema(many=True).dump([]))

        assert "data" in data
        assert type(data["data"]) is list
        assert len(data["data"]) == 0
        assert "links" in data
        assert data["links"]["self"] == "/authors/"


class TestCompoundDocuments:
    def test_include_data_with_many(self, post):
        data = unpack(
            PostSchema(include_data=("post_comments", "post_comments.author")).dump(
                post
            )
        )
        assert "included" in data
        assert len(data["included"]) == 4
        first_comment = [i for i in data["included"] if i["type"] == "comments"][0]
        assert "attributes" in first_comment
        assert "body" in first_comment["attributes"]

    def test_include_data_with_single(self, post):
        data = unpack(PostSchema(include_data=("author",)).dump(post))
        assert "included" in data
        assert len(data["included"]) == 1
        author = data["included"][0]
        assert "attributes" in author
        assert "first_name" in author["attributes"]

    def test_include_data_with_all_relations(self, post):
        data = unpack(
            PostSchema(
                include_data=("author", "post_comments", "post_comments.author")
            ).dump(post)
        )
        assert "included" in data
        assert len(data["included"]) == 5
        for included in data["included"]:
            assert included["id"]
            assert included["type"] in ("people", "comments")
        expected_comments_author_ids = {
            str(comment.author.id) for comment in post.comments
        }
        included_comments_author_ids = {
            i["id"]
            for i in data["included"]
            if i["type"] == "people" and i["id"] != str(post.author.id)
        }
        assert included_comments_author_ids == expected_comments_author_ids

    def test_include_no_data(self, post):
        data = unpack(PostSchema(include_data=()).dump(post))
        assert "included" not in data

    def test_include_self_referential_relationship(self):
        class RefSchema(Schema):
            id = fields.Int()
            data = fields.Str()
            parent = fields.Relationship(schema="self", many=False)

            class Meta:
                type_ = "refs"

        obj = {"id": 1, "data": "data1", "parent": {"id": 2, "data": "data2"}}
        data = unpack(RefSchema(include_data=("parent",)).dump(obj))
        assert "included" in data
        assert data["included"][0]["attributes"]["data"] == "data2"

    def test_include_self_referential_relationship_many(self):
        class RefSchema(Schema):
            id = fields.Str()
            data = fields.Str()
            children = fields.Relationship(schema="self", many=True)

            class Meta:
                type_ = "refs"

        obj = {
            "id": "1",
            "data": "data1",
            "children": [{"id": "2", "data": "data2"}, {"id": "3", "data": "data3"}],
        }
        data = unpack(RefSchema(include_data=("children",)).dump(obj))
        assert "included" in data
        assert len(data["included"]) == 2
        for child in data["included"]:
            assert child["attributes"]["data"] == "data%s" % child["id"]

    def test_include_self_referential_relationship_many_deep(self):
        class RefSchema(Schema):
            id = fields.Str()
            data = fields.Str()
            children = fields.Relationship(schema="self", type_="refs", many=True)

            class Meta:
                type_ = "refs"

        obj = {
            "id": "1",
            "data": "data1",
            "children": [
                {"id": "2", "data": "data2", "children": []},
                {
                    "id": "3",
                    "data": "data3",
                    "children": [
                        {"id": "4", "data": "data4", "children": []},
                        {"id": "5", "data": "data5", "children": []},
                    ],
                },
            ],
        }
        data = unpack(RefSchema(include_data=("children",)).dump(obj))
        assert "included" in data
        assert len(data["included"]) == 4
        for child in data["included"]:
            assert child["attributes"]["data"] == "data%s" % child["id"]

    def test_include_data_with_many_and_schema_as_class(self, post):
        class PostClassSchema(PostSchema):
            post_comments = fields.Relationship(
                "http://test.test/posts/{id}/comments/",
                related_url_kwargs={"id": "<id>"},
                attribute="comments",
                dump_to="post-comments",
                schema=CommentSchema,
                many=True,
            )

            class Meta(PostSchema.Meta):
                pass

        data = unpack(PostClassSchema(include_data=("post_comments",)).dump(post))
        assert "included" in data
        assert len(data["included"]) == 2
        first_comment = data["included"][0]
        assert "attributes" in first_comment
        assert "body" in first_comment["attributes"]

    def test_include_data_with_nested_only_arg(self, post):
        data = unpack(
            PostSchema(
                only=(
                    "id",
                    "post_comments.id",
                    "post_comments.author.id",
                    "post_comments.author.twitter",
                ),
                include_data=("post_comments", "post_comments.author"),
            ).dump(post)
        )

        assert "included" in data
        assert len(data["included"]) == 4

        first_author = [i for i in data["included"] if i["type"] == "people"][0]
        assert "twitter" in first_author["attributes"]
        for attribute in ("first_name", "last_name"):
            assert attribute not in first_author["attributes"]

    def test_include_data_with_nested_exclude_arg(self, post):
        data = unpack(
            PostSchema(
                exclude=("post_comments.author.twitter",),
                include_data=("post_comments", "post_comments.author"),
            ).dump(post)
        )

        assert "included" in data
        assert len(data["included"]) == 4

        first_author = [i for i in data["included"] if i["type"] == "people"][0]
        assert "twitter" not in first_author["attributes"]
        for attribute in ("first_name", "last_name"):
            assert attribute in first_author["attributes"]

    def test_include_data_load(self, post):
        serialized = unpack(
            PostSchema(
                include_data=("author", "post_comments", "post_comments.author")
            ).dump(post)
        )
        loaded = unpack(PostSchema().load(serialized))

        assert "author" in loaded
        assert loaded["author"]["id"] == str(post.author.id)
        assert loaded["author"]["first_name"] == post.author.first_name

        assert "comments" in loaded
        assert len(loaded["comments"]) == len(post.comments)
        for comment in loaded["comments"]:
            assert "body" in comment
            assert comment["id"] in [str(c.id) for c in post.comments]

    def test_include_data_load_null(self, post_with_null_author):
        serialized = unpack(
            PostSchema(include_data=("author", "post_comments")).dump(
                post_with_null_author
            )
        )

        with pytest.raises(ValidationError) as excinfo:
            PostSchema().load(serialized)
        err = excinfo.value
        assert "author" in err.args[0]

    def test_include_data_load_without_schema_loads_only_ids(self, post):
        class PostInnerSchemalessSchema(Schema):
            id = fields.Str()
            comments = fields.Relationship(
                "http://test.test/posts/{id}/comments/",
                related_url_kwargs={"id": "<id>"},
                data_key="post-comments",
                load_from="post-comments",
                many=True,
                type_="comments",
            )

            class Meta:
                type_ = "posts"
                strict = True

        serialized = unpack(
            PostSchema(include_data=("author", "post_comments")).dump(post)
        )

        if _MARSHMALLOW_VERSION_INFO[0] >= 3:
            from marshmallow import INCLUDE

            load_kwargs = {"unknown": INCLUDE}
        else:
            load_kwargs = {}

        loaded = unpack(PostInnerSchemalessSchema(**load_kwargs).load(serialized))

        assert "comments" in loaded
        assert len(loaded["comments"]) == len(post.comments)
        for comment_id in loaded["comments"]:
            assert int(comment_id) in [c.id for c in post.comments]

    def test_include_data_with_schema_context(self, post):
        class ContextTestSchema(Schema):
            id = fields.Str()
            from_context = fields.Method("get_from_context")

            def get_from_context(self, obj):
                return self.context["some_value"]

            class Meta:
                type_ = "people"

        class PostContextTestSchema(PostSchema):
            author = fields.Relationship(
                "http://test.test/posts/{id}/author/",
                related_url_kwargs={"id": "<id>"},
                schema=ContextTestSchema,
                many=False,
            )

            class Meta(PostSchema.Meta):
                pass

        serialized = unpack(
            PostContextTestSchema(
                include_data=("author",), context={"some_value": "Hello World"}
            ).dump(post)
        )

        for included in serialized["included"]:
            if included["type"] == "people":
                assert "from_context" in included["attributes"]
                assert included["attributes"]["from_context"] == "Hello World"


def get_error_by_field(errors, field):
    for err in errors["errors"]:
        # Relationship error pointers won't match with this.
        if err["source"]["pointer"].endswith("/" + field):
            return err
    return None


class TestErrorFormatting:
    def test_validate(self):
        author = make_serialized_author({"first_name": "Dan", "password": "short"})
        try:
            errors = AuthorSchema().validate(author)
        except ValidationError as err:  # marshmallow 2
            errors = err.messages
        assert "errors" in errors
        assert len(errors["errors"]) == 2

        password_err = get_error_by_field(errors, "password")
        assert password_err
        assert password_err["detail"] == "Shorter than minimum length 6."

        lname_err = get_error_by_field(errors, "last_name")
        assert lname_err
        assert lname_err["detail"] == "Missing data for required field."

    def test_errors_in_strict_mode(self):
        author = make_serialized_author({"first_name": "Dan", "password": "short"})
        with pytest.raises(ValidationError) as excinfo:
            AuthorSchema().load(author)
        errors = excinfo.value.messages
        assert "errors" in errors
        assert len(errors["errors"]) == 2
        password_err = get_error_by_field(errors, "password")
        assert password_err
        assert password_err["detail"] == "Shorter than minimum length 6."

        lname_err = get_error_by_field(errors, "last_name")
        assert lname_err
        assert lname_err["detail"] == "Missing data for required field."

    def test_no_type_raises_error(self):
        author = {
            "data": {"attributes": {"first_name": "Dan", "password": "supersecure"}}
        }
        with pytest.raises(ValidationError) as excinfo:
            AuthorSchema().load(author)

        expected = {
            "errors": [
                {
                    "detail": "`data` object must include `type` key.",
                    "source": {"pointer": "/data"},
                }
            ]
        }
        assert excinfo.value.messages == expected

        # This assertion is only valid on newer versions of marshmallow, which
        # have this bugfix: https://github.com/marshmallow-code/marshmallow/pull/530
        if _MARSHMALLOW_VERSION_INFO >= (2, 10, 1):
            try:
                errors = AuthorSchema().validate(author)
            except ValidationError as err:  # marshmallow 2
                errors = err.messages
            assert errors == expected

    def test_validate_no_data_raises_error(self):
        author = {"meta": {"this": "that"}}

        with pytest.raises(ValidationError) as excinfo:
            AuthorSchema().load(author)

        errors = excinfo.value.messages

        expected = {
            "errors": [
                {
                    "detail": "Object must include `data` key.",
                    "source": {"pointer": "/"},
                }
            ]
        }

        assert errors == expected

    def test_validate_type(self):
        author = {
            "data": {
                "type": "invalid",
                "attributes": {"first_name": "Dan", "password": "supersecure"},
            }
        }
        with pytest.raises(IncorrectTypeError) as excinfo:
            AuthorSchema().validate(author)
        assert excinfo.value.args[0] == 'Invalid type. Expected "people".'
        assert excinfo.value.messages == {
            "errors": [
                {
                    "detail": 'Invalid type. Expected "people".',
                    "source": {"pointer": "/data/type"},
                }
            ]
        }

    def test_validate_id(self):
        """ the pointer for id should be at the data object, not attributes """
        author = {
            "data": {
                "type": "people",
                "id": 123,
                "attributes": {"first_name": "Rob", "password": "correcthorses"},
            }
        }
        try:
            errors = AuthorSchema().validate(author)
        except ValidationError as err:
            errors = err.messages
        assert "errors" in errors
        assert len(errors["errors"]) == 2

        lname_err = get_error_by_field(errors, "last_name")
        assert lname_err
        assert lname_err["source"]["pointer"] == "/data/attributes/last_name"
        assert lname_err["detail"] == "Missing data for required field."

        id_err = get_error_by_field(errors, "id")
        assert id_err
        assert id_err["source"]["pointer"] == "/data/id"
        assert id_err["detail"] == "Not a valid string."

    def test_load(self):
        with pytest.raises(ValidationError) as excinfo:
            AuthorSchema().load(
                make_serialized_author({"first_name": "Dan", "password": "short"})
            )
        errors = excinfo.value.messages
        assert "errors" in errors
        assert len(errors["errors"]) == 2

        password_err = get_error_by_field(errors, "password")
        assert password_err
        assert password_err["detail"] == "Shorter than minimum length 6."

        lname_err = get_error_by_field(errors, "last_name")
        assert lname_err
        assert lname_err["detail"] == "Missing data for required field."

    def test_errors_is_empty_if_valid(self):
        errors = AuthorSchema().validate(
            make_serialized_author(
                {
                    "first_name": "Dan",
                    "last_name": "Gebhardt",
                    "password": "supersecret",
                }
            )
        )
        assert errors == {}

    def test_errors_many(self):
        authors = make_serialized_authors(
            [
                {"first_name": "Dan", "last_name": "Gebhardt", "password": "bad"},
                {
                    "first_name": "Dan",
                    "last_name": "Gebhardt",
                    "password": "supersecret",
                },
            ]
        )
        try:
            errors = AuthorSchema(many=True).validate(authors)["errors"]
        except ValidationError as err:
            errors = err.messages["errors"]

        assert len(errors) == 1

        err = errors[0]
        assert "source" in err
        assert err["source"]["pointer"] == "/data/0/attributes/password"

    def test_errors_many_not_list(self):
        authors = make_serialized_author(
            {"first_name": "Dan", "last_name": "Gebhardt", "password": "bad"}
        )
        try:
            errors = AuthorSchema(many=True).validate(authors)["errors"]
        except ValidationError as err:
            errors = err.messages["errors"]

        assert len(errors) == 1

        err = errors[0]
        assert "source" in err
        assert err["source"]["pointer"] == "/data"
        assert err["detail"] == "`data` expected to be a collection."

    def test_many_id_errors(self):
        """ the pointer for id should be at the data object, not attributes """
        author = {
            "data": [
                {
                    "type": "people",
                    "id": "invalid",
                    "attributes": {"first_name": "Rob", "password": "correcthorses"},
                },
                {
                    "type": "people",
                    "id": 37,
                    "attributes": {
                        "first_name": "Dan",
                        "last_name": "Gebhardt",
                        "password": "supersecret",
                    },
                },
            ]
        }
        try:
            errors = AuthorSchema(many=True).validate(author)
        except ValidationError as err:  # marshmallow 2
            errors = err.messages
        assert "errors" in errors
        assert len(errors["errors"]) == 2

        lname_err = get_error_by_field(errors, "last_name")
        assert lname_err
        assert lname_err["source"]["pointer"] == "/data/0/attributes/last_name"
        assert lname_err["detail"] == "Missing data for required field."

        id_err = get_error_by_field(errors, "id")
        assert id_err
        assert id_err["source"]["pointer"] == "/data/1/id"
        assert id_err["detail"] == "Not a valid string."

    def test_nested_fields_error(self):
        min_size = 10

        class ThirdLevel(ma.Schema):
            number = fields.Int(required=True, validate=ma.validate.Range(min=min_size))

        class SecondLevel(ma.Schema):
            foo = fields.Str(required=True)
            third = fields.Nested(ThirdLevel)

        class FirstLevel(Schema):
            class Meta:
                type_ = "first"

            id = fields.Int()
            second = fields.Nested(SecondLevel)

        schema = FirstLevel()
        result = schema.validate(
            {
                "data": {
                    "type": "first",
                    "attributes": {"second": {"third": {"number": 5}}},
                }
            }
        )

        def sort_func(d):
            return d["source"]["pointer"]

        expected_errors = sorted(
            [
                {
                    "source": {"pointer": "/data/attributes/second/third/number"},
                    "detail": f"Must be greater than or equal to {min_size}."
                    if _MARSHMALLOW_VERSION_INFO[0] >= 3
                    else f"Must be at least {min_size}.",
                },
                {
                    "source": {"pointer": "/data/attributes/second/foo"},
                    "detail": ma.fields.Field.default_error_messages["required"],
                },
            ],
            key=sort_func,
        )

        errors = sorted(result["errors"], key=sort_func)

        assert errors == expected_errors


class TestMeta:
    shape = {
        "id": 1,
        "sides": 3,
        "meta": "triangle",
        "resource_meta": {"concave": False},
        "document_meta": {"page": 1},
    }

    shapes = [
        {
            "id": 1,
            "sides": 3,
            "meta": "triangle",
            "resource_meta": {"concave": False},
            "document_meta": {"page": 1},
        },
        {
            "id": 2,
            "sides": 4,
            "meta": "quadrilateral",
            "resource_meta": {"concave": True},
            "document_meta": {"page": 1},
        },
    ]

    def test_dump_single(self):
        serialized = unpack(PolygonSchema().dump(self.shape))
        assert "meta" in serialized
        assert serialized["meta"] == self.shape["document_meta"]
        assert serialized["data"]["attributes"]["meta"] == self.shape["meta"]
        assert serialized["data"]["meta"] == self.shape["resource_meta"]

    def test_dump_many(self):
        serialized = unpack(PolygonSchema(many=True).dump(self.shapes))
        assert "meta" in serialized
        assert serialized["meta"] == self.shapes[0]["document_meta"]

        first = serialized["data"][0]
        assert first["attributes"]["meta"] == self.shapes[0]["meta"]
        assert first["meta"] == self.shapes[0]["resource_meta"]

        second = serialized["data"][1]
        assert second["attributes"]["meta"] == self.shapes[1]["meta"]
        assert second["meta"] == self.shapes[1]["resource_meta"]

    def test_load_single(self):
        serialized = unpack(PolygonSchema().dump(self.shape))
        loaded = unpack(PolygonSchema().load(serialized))

        assert loaded["meta"] == self.shape["meta"]
        assert loaded["resource_meta"] == self.shape["resource_meta"]
        assert loaded["document_meta"] == self.shape["document_meta"]

    def test_load_many(self):
        serialized = unpack(PolygonSchema(many=True).dump(self.shapes))
        loaded = unpack(PolygonSchema(many=True).load(serialized))

        first = loaded[0]
        assert first["meta"] == self.shapes[0]["meta"]
        assert first["resource_meta"] == self.shapes[0]["resource_meta"]
        assert first["document_meta"] == self.shapes[0]["document_meta"]

        second = loaded[1]
        assert second["meta"] == self.shapes[1]["meta"]
        assert second["resource_meta"] == self.shapes[1]["resource_meta"]
        assert second["document_meta"] == self.shapes[1]["document_meta"]


def assert_relationship_error(pointer, errors):
    """Walk through the dictionary and determine if a specific
    relationship pointer exists
    """
    pointer = f"/data/relationships/{pointer}/data"
    for error in errors:
        if pointer == error["source"]["pointer"]:
            return True
    return False


class TestRelationshipLoading:
    article = {
        "data": {
            "id": "1",
            "type": "articles",
            "attributes": {"body": "Test"},
            "relationships": {
                "author": {"data": {"type": "people", "id": "1"}},
                "comments": {"data": [{"type": "comments", "id": "1"}]},
            },
        }
    }

    def test_deserializing_relationship_fields(self):
        data = unpack(ArticleSchema().load(self.article))
        assert data["body"] == "Test"
        assert data["author"] == "1"
        assert data["comments"] == ["1"]

    def test_deserializing_nested_relationship_fields(self):
        class RelationshipWithSchemaCommentSchema(Schema):
            id = fields.Str()
            body = fields.Str(required=True)
            author = fields.Relationship(
                schema=AuthorSchema, many=False, type_="people"
            )

            class Meta:
                type_ = "comments"
                strict = True

        class RelationshipWithSchemaArticleSchema(Schema):
            id = fields.Integer()
            body = fields.String()
            comments = fields.Relationship(
                schema=RelationshipWithSchemaCommentSchema, many=True, type_="comments"
            )
            author = fields.Relationship(
                dump_only=False,
                include_resource_linkage=True,
                many=False,
                type_="people",
            )

            class Meta:
                type_ = "articles"
                strict = True

        article = self.article.copy()
        article["included"] = [
            {
                "id": "1",
                "type": "comments",
                "attributes": {"body": "Test comment"},
                "relationships": {"author": {"data": {"type": "people", "id": "2"}}},
            },
            {
                "id": "2",
                "type": "people",
                "attributes": {"first_name": "Marshmallow Jr", "last_name": "JsonAPI"},
            },
        ]

        included_author = filter(
            lambda item: item["type"] == "people", article["included"]
        )
        included_author = list(included_author)[0]

        data = unpack(RelationshipWithSchemaArticleSchema().load(article))
        author = data["comments"][0]["author"]

        assert isinstance(author, dict)
        assert author["first_name"] == included_author["attributes"]["first_name"]

    def test_deserializing_relationship_errors(self):
        data = self.article
        data["data"]["relationships"]["author"]["data"] = {}
        data["data"]["relationships"]["comments"]["data"] = [{}]
        with pytest.raises(ValidationError) as excinfo:
            ArticleSchema().load(data)
        errors = excinfo.value.messages

        assert assert_relationship_error("author", errors["errors"])
        assert assert_relationship_error("comments", errors["errors"])

    def test_deserializing_missing_required_relationship(self):
        class ArticleSchemaRequiredRelationships(Schema):
            id = fields.Integer()
            body = fields.String()
            author = fields.Relationship(
                dump_only=False,
                include_resource_linkage=True,
                many=False,
                type_="people",
                required=True,
            )
            comments = fields.Relationship(
                dump_only=False,
                include_resource_linkage=True,
                many=True,
                type_="comments",
                required=True,
            )

            class Meta:
                type_ = "articles"
                strict = True

        article = self.article.copy()
        article["data"]["relationships"] = {}

        with pytest.raises(ValidationError) as excinfo:
            unpack(ArticleSchemaRequiredRelationships().load(article))
        errors = excinfo.value.messages

        assert assert_relationship_error("author", errors["errors"])
        assert assert_relationship_error("comments", errors["errors"])

    def test_deserializing_relationship_with_missing_param(self):
        if _MARSHMALLOW_VERSION_INFO[0] >= 3:
            author_missing = "1"
            comments_missing = ["2", "3"]
        else:
            author_missing = {"data": {"type": "people", "id": "1"}}
            comments_missing = {
                "data": [
                    {"type": "comments", "id": "2"},
                    {"type": "comments", "id": "3"},
                ]
            }

        class ArticleMissingParamSchema(Schema):
            id = fields.Integer()
            body = fields.String()
            author = fields.Relationship(
                dump_only=False,
                include_resource_linkage=True,
                many=False,
                type_="people",
                missing=author_missing,
            )
            comments = fields.Relationship(
                dump_only=False,
                include_resource_linkage=True,
                many=True,
                type_="comments",
                missing=comments_missing,
            )

            class Meta:
                type_ = "articles"
                strict = True

        article = self.article.copy()
        article["data"]["relationships"] = {}

        data = unpack(ArticleMissingParamSchema().load(article))

        assert "author" in data
        assert data["author"] == "1"
        assert "comments" in data
        assert data["comments"] == ["2", "3"]
