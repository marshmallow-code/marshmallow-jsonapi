from hashlib import md5

from faker import Factory
from marshmallow import validate

from marshmallow_jsonapi import Schema, fields

fake = Factory.create()


class Bunch:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


class Post(Bunch):
    pass


class Author(Bunch):
    pass


class Comment(Bunch):
    pass


class Keyword(Bunch):
    pass


class AuthorSchema(Schema):
    id = fields.Str()
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    password = fields.Str(load_only=True, validate=validate.Length(6))
    twitter = fields.Str()

    def get_top_level_links(self, data, many):
        if many:
            self_link = "/authors/"
        else:
            self_link = "/authors/{}".format(data["id"])
        return {"self": self_link}

    class Meta:
        type_ = "people"


class KeywordSchema(Schema):
    id = fields.Str()
    keyword = fields.Str(required=True)

    def get_attribute(self, attr, obj, default):
        if obj == "id":
            return md5(
                super(Schema, self)
                .get_attribute(attr, "keyword", default)
                .encode("utf-8")
            ).hexdigest()
        else:
            return super(Schema, self).get_attribute(attr, obj, default)

    class Meta:
        type_ = "keywords"
        strict = True


class CommentSchema(Schema):
    id = fields.Str()
    body = fields.Str(required=True)

    author = fields.Relationship(
        "http://test.test/comments/{id}/author/",
        related_url_kwargs={"id": "<id>"},
        schema=AuthorSchema,
        many=False,
    )

    class Meta:
        type_ = "comments"
        strict = True


class ArticleSchema(Schema):
    id = fields.Integer()
    body = fields.String()
    author = fields.Relationship(
        dump_only=False, include_resource_linkage=True, many=False, type_="people"
    )
    comments = fields.Relationship(
        dump_only=False, include_resource_linkage=True, many=True, type_="comments"
    )

    class Meta:
        type_ = "articles"
        strict = True


class PostSchema(Schema):
    id = fields.Str()
    post_title = fields.Str(attribute="title", data_key="title")

    author = fields.Relationship(
        "http://test.test/posts/{id}/author/",
        related_url_kwargs={"id": "<id>"},
        schema=AuthorSchema,
        many=False,
        type_="people",
    )

    post_comments = fields.Relationship(
        "http://test.test/posts/{id}/comments/",
        related_url_kwargs={"id": "<id>"},
        attribute="comments",
        data_key="post-comments",
        schema="CommentSchema",
        many=True,
        type_="comments",
    )

    post_keywords = fields.Relationship(
        "http://test.test/posts/{id}/keywords/",
        related_url_kwargs={"id": "<id>"},
        attribute="keywords",
        data_key="post-keywords",
        schema="KeywordSchema",
        many=True,
        type_="keywords",
    )

    class Meta:
        type_ = "posts"
        strict = True


class PolygonSchema(Schema):
    id = fields.Integer(as_string=True)
    sides = fields.Integer()
    # This is an attribute that uses the 'meta' key: /data/attributes/meta
    meta = fields.String()
    # This is the document's top level meta object: /meta
    document_meta = fields.DocumentMeta()
    # This is the resource object's meta object: /data/meta
    resource_meta = fields.ResourceMeta()

    class Meta:
        type_ = "shapes"
        strict = True
