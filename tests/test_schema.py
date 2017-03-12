#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from marshmallow import validate, ValidationError
from marshmallow_jsonapi import Schema, fields
from marshmallow_jsonapi.exceptions import IncorrectTypeError
from marshmallow_jsonapi.utils import _MARSHMALLOW_VERSION_INFO

class AuthorSchema(Schema):
    id = fields.Int()
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    password = fields.Str(load_only=True, validate=validate.Length(6))
    twitter = fields.Str()

    def get_top_level_links(self, data, many):
        if many:
            self_link = '/authors/'
        else:
            self_link = '/authors/{}'.format(data['id'])
        return {'self': self_link}

    class Meta:
        type_ = 'people'


class PostSchema(Schema):
    id = fields.Int()
    post_title = fields.Str(attribute='title', dump_to='title')

    author = fields.Relationship(
        'http://test.test/posts/{id}/author/',
        related_url_kwargs={'id': '<id>'},
        schema=AuthorSchema, many=False
    )

    post_comments = fields.Relationship(
        'http://test.test/posts/{id}/comments/',
        related_url_kwargs={'id': '<id>'},
        attribute='comments', dump_to='post-comments',
        schema='CommentSchema', many=True
    )

    class Meta:
        type_ = 'posts'


class CommentSchema(Schema):
    id = fields.Int()
    body = fields.Str(required=True)

    class Meta:
        type_ = 'comments'


def test_type_is_required():
    class BadSchema(Schema):
        id = fields.Str()

        class Meta:
            pass

    with pytest.raises(ValueError) as excinfo:
        BadSchema()
    assert excinfo.value.args[0] == 'Must specify type_ class Meta option'

def test_id_field_is_required():
    class BadSchema(Schema):

        class Meta:
            type_ = 'users'

    with pytest.raises(ValueError) as excinfo:
        BadSchema()
    assert excinfo.value.args[0] == 'Must have an `id` field'

class TestResponseFormatting:

    def test_dump_single(self, author):
        data = AuthorSchema().dump(author).data

        assert 'data' in data
        assert type(data['data']) is dict

        assert data['data']['id'] == author.id
        assert data['data']['type'] == 'people'
        attribs = data['data']['attributes']

        assert attribs['first_name'] == author.first_name
        assert attribs['last_name'] == author.last_name

    def test_dump_many(self, authors):
        data = AuthorSchema(many=True).dump(authors).data
        assert 'data' in data
        assert type(data['data']) is list

        first = data['data'][0]
        assert first['id'] == authors[0].id
        assert first['type'] == 'people'

        attribs = first['attributes']

        assert attribs['first_name'] == authors[0].first_name
        assert attribs['last_name'] == authors[0].last_name

    def test_self_link_single(self, author):
        data = AuthorSchema().dump(author).data
        assert 'links' in data
        assert data['links']['self'] == '/authors/{}'.format(author.id)

    def test_self_link_many(self, authors):
        data = AuthorSchema(many=True).dump(authors).data
        assert 'links' in data
        assert data['links']['self'] == '/authors/'

    def test_dump_to(self, post):
        data = PostSchema().dump(post).data
        assert 'data' in data
        assert 'attributes' in data['data']
        assert 'title' in data['data']['attributes']
        assert 'relationships' in data['data']
        assert 'post-comments' in data['data']['relationships']

    def test_dump_none(self):
        data = AuthorSchema().dump(None).data

        assert 'data' in data
        assert data['data'] is None
        assert 'links' not in data

    def test_dump_empty_list(self):
        data = AuthorSchema(many=True).dump([]).data

        assert 'data' in data
        assert type(data['data']) is list
        assert len(data['data']) == 0
        assert 'links' in data
        assert data['links']['self'] == '/authors/'


class TestCompoundDocuments:

    def test_include_data_with_many(self, post):
        data = PostSchema(include_data=('post_comments',)).dump(post).data
        assert 'included' in data
        assert len(data['included']) == 2
        first_comment = data['included'][0]
        assert 'attributes' in first_comment
        assert 'body' in first_comment['attributes']

    def test_include_data_with_single(self, post):
        data = PostSchema(include_data=('author',)).dump(post).data
        assert 'included' in data
        assert len(data['included']) == 1
        author = data['included'][0]
        assert 'attributes' in author
        assert 'first_name' in author['attributes']

    def test_include_data_with_all_relations(self, post):
        data = PostSchema(include_data=('author', 'post_comments')).dump(post).data
        assert 'included' in data
        assert len(data['included']) == 3
        for included in data['included']:
            assert included['id']
            assert included['type'] in ('people', 'comments')

    def test_include_no_data(self, post):
        data = PostSchema(include_data=()).dump(post).data
        assert 'included' not in data

    def test_include_self_referential_relationship(self):
        class RefSchema(Schema):
            id = fields.Int()
            data = fields.Str()
            parent = fields.Relationship(schema='self', many=False)

            class Meta:
                type_ = 'refs'

        obj = {
            'id': 1, 'data': 'data1',
            'parent': {
                'id': 2,
                'data': 'data2'
            }
        }
        data = RefSchema(include_data=('parent',)).dump(obj).data
        assert 'included' in data
        assert data['included'][0]['attributes']['data'] == 'data2'

    def test_include_self_referential_relationship_many(self):
        class RefSchema(Schema):
            id = fields.Str()
            data = fields.Str()
            children = fields.Relationship(schema='self', many=True)

            class Meta:
                type_ = 'refs'

        obj = {
            'id': '1',
            'data': 'data1',
            'children': [
                {
                    'id': '2',
                    'data': 'data2'
                },
                {
                    'id': '3',
                    'data': 'data3'
                }
            ]
        }
        data = RefSchema(include_data=('children', )).dump(obj).data
        assert 'included' in data
        assert len(data['included']) == 2
        for child in data['included']:
            assert child['attributes']['data'] == 'data%s' % child['id']

    def test_include_self_referential_relationship_many_deep(self):
        class RefSchema(Schema):
            id = fields.Str()
            data = fields.Str()
            children = fields.Relationship(schema='self', type_='refs',
                                           many=True)

            class Meta:
                type_ = 'refs'

        obj = {
            'id': '1',
            'data': 'data1',
            'children': [
                {
                    'id': '2',
                    'data': 'data2',
                    'children': [],
                },
                {
                    'id': '3',
                    'data': 'data3',
                    'children': [
                        {
                            'id': '4',
                            'data': 'data4',
                            'children': []
                        },
                        {
                            'id': '5',
                            'data': 'data5',
                            'children': []
                        }
                    ]
                }
            ]
        }
        data = RefSchema(include_data=('children', )).dump(obj).data
        assert 'included' in data
        assert len(data['included']) == 4
        for child in data['included']:
            assert child['attributes']['data'] == 'data%s' % child['id']

    def test_include_data_with_many_and_schema_as_class(self, post):
        class PostClassSchema(PostSchema):
            post_comments = fields.Relationship(
                'http://test.test/posts/{id}/comments/',
                related_url_kwargs={'id': '<id>'},
                attribute='comments', dump_to='post-comments',
                schema=CommentSchema, many=True
            )

            class Meta(PostSchema.Meta):
                pass

        data = PostClassSchema(include_data=('post_comments',)).dump(post).data
        assert 'included' in data
        assert len(data['included']) == 2
        first_comment = data['included'][0]
        assert 'attributes' in first_comment
        assert 'body' in first_comment['attributes']


def get_error_by_field(errors, field):
    for err in errors['errors']:
        if err['source']['pointer'].split('/data/attributes/')[1] == field:
            return err
    return None

def make_author(attributes, type_='people'):
    return {
        'data': {
            'type': type_,
            'attributes': attributes,
        }
    }

def make_authors(items, type_='people'):
    return {
        'data': [
            {'type': type_, 'attributes': each} for each in items
        ]
    }

class TestErrorFormatting:

    def test_validate(self):
        author = make_author({'first_name': 'Dan', 'password': 'short'})
        errors = AuthorSchema().validate(author)
        assert 'errors' in errors
        assert len(errors['errors']) == 2

        password_err = get_error_by_field(errors, 'password')
        assert password_err
        assert password_err['detail'] == 'Shorter than minimum length 6.'

        lname_err = get_error_by_field(errors, 'last_name')
        assert lname_err
        assert lname_err['detail'] == 'Missing data for required field.'

    def test_validate_in_strict_mode(self):
        author = make_author({'first_name': 'Dan', 'password': 'short'})
        try:
            AuthorSchema(strict=True).validate(author)
        except ValidationError as err:
            errors = err.messages
            assert 'errors' in errors
            assert len(errors['errors']) == 2
            password_err = get_error_by_field(errors, 'password')
            assert password_err
            assert password_err['detail'] == 'Shorter than minimum length 6.'

            lname_err = get_error_by_field(errors, 'last_name')
            assert lname_err
            assert lname_err['detail'] == 'Missing data for required field.'
        else:
            assert False, 'No validation error raised'

    def test_validate_no_type_raises_error(self):
        author = {'data': {'attributes': {'first_name': 'Dan', 'password': 'supersecure'}}}
        with pytest.raises(ValidationError) as excinfo:
            AuthorSchema(strict=True).validate(author)

        expected = {
            'errors': [
                {
                    'detail': '`data` object must include `type` key.',
                    'source': {
                        'pointer': '/data'
                    }
                }
            ]
        }
        assert excinfo.value.messages == expected

        # This assertion is only valid on newer versions of marshmallow, which
        # have this bugfix: https://github.com/marshmallow-code/marshmallow/pull/530
        if _MARSHMALLOW_VERSION_INFO >= (2, 10, 1):
            errors = AuthorSchema(strict=False).validate(author)
            assert errors == expected

    def test_validate_no_data_raises_error(self):
        author = {'meta': {'this': 'that'}}

        with pytest.raises(ValidationError) as excinfo:
            AuthorSchema(strict=True).validate(author)

        errors = excinfo.value.messages

        expected = {
            'errors': [
                {
                    'detail': 'Object must include `data` key.',
                    'source': {
                        'pointer': '/'
                    }
                }
            ]
        }

        assert errors == expected

    def test_validate_type(self):
        author = {'data':
                {'type': 'invalid', 'attributes': {'first_name': 'Dan', 'password': 'supersecure'}}}
        with pytest.raises(IncorrectTypeError) as excinfo:
            AuthorSchema().validate(author)
        assert excinfo.value.args[0] == 'Invalid type. Expected "people".'
        assert excinfo.value.messages == {
            'errors': [
                {
                    'detail': 'Invalid type. Expected "people".',
                    'source': {
                        'pointer': '/data/type'
                    }
                }
            ]
        }

    def test_load(self):
        _, errors = AuthorSchema().load(make_author({'first_name': 'Dan', 'password': 'short'}))
        assert 'errors' in errors
        assert len(errors['errors']) == 2

        password_err = get_error_by_field(errors, 'password')
        assert password_err
        assert password_err['detail'] == 'Shorter than minimum length 6.'

        lname_err = get_error_by_field(errors, 'last_name')
        assert lname_err
        assert lname_err['detail'] == 'Missing data for required field.'

    def test_errors_is_empty_if_valid(self):
        errors = AuthorSchema().validate(
            make_author({'first_name': 'Dan', 'last_name': 'Gebhardt', 'password': 'supersecret'}))
        assert errors == {}

    def test_errors_many(self):
        authors = make_authors([
            {'first_name': 'Dan', 'last_name': 'Gebhardt', 'password': 'supersecret'},
            {'first_name': 'Dan', 'last_name': 'Gebhardt', 'password': 'bad'},
        ])
        errors = AuthorSchema(many=True).validate(authors)['errors']

        assert len(errors) == 1

        err = errors[0]
        assert 'source' in err
        assert err['source']['pointer'] == '/data/1/attributes/password'

def dasherize(text):
    return text.replace('_', '-')


class TestInflection:

    class AuthorSchemaWithInflection(Schema):
        id = fields.Int(dump_only=True)
        first_name = fields.Str(required=True, validate=validate.Length(min=2))
        last_name = fields.Str(required=True)

        class Meta:
            type_ = 'people'
            inflect = dasherize

    @pytest.fixture()
    def schema(self):
        return self.AuthorSchemaWithInflection()

    def test_dump(self, schema, author):
        data = schema.dump(author).data

        assert data['data']['id'] == author.id
        assert data['data']['type'] == 'people'
        attribs = data['data']['attributes']

        assert 'first-name' in attribs
        assert 'last-name' in attribs

        assert attribs['first-name'] == author.first_name
        assert attribs['last-name'] == author.last_name

    def test_validate_with_inflection(self, schema):
        errors = schema.validate(make_author({'first-name': 'd'}))
        lname_err = get_error_by_field(errors, 'last-name')
        assert lname_err
        assert lname_err['detail'] == 'Missing data for required field.'

        fname_err = get_error_by_field(errors, 'first-name')
        assert fname_err
        assert fname_err['detail'] == 'Shorter than minimum length 2.'

    def test_load_with_inflection(self, schema):
        # invalid
        data, errors = schema.load(make_author({'first-name': 'd'}))
        fname_err = get_error_by_field(errors, 'first-name')
        assert fname_err
        assert fname_err['detail'] == 'Shorter than minimum length 2.'

        # valid
        data, errors = schema.load(make_author({'first-name': 'Dan'}))
        assert data['first_name'] == 'Dan'

    def test_load_with_inflection_and_load_from_override(self):
        class AuthorSchemaWithInflection2(Schema):
            id = fields.Str(dump_only=True)
            # load_from takes precedence over inflected attribute
            first_name = fields.Str(load_from='firstName')
            last_name = fields.Str()

            class Meta:
                type_ = 'people'
                inflect = dasherize

        sch = AuthorSchemaWithInflection2()

        data, errs = sch.load(make_author({'firstName': 'Steve', 'last-name': 'Loria'}))
        assert not errs
        assert data['first_name'] == 'Steve'
        assert data['last_name'] == 'Loria'

    def test_load_bulk_id_fields(self):
        request = {'data': [{'id': 1, 'type': 'people'}]}

        result, err = AuthorSchema(only=('id',), many=True).load(request)
        assert err == {}
        assert type(result) is list

        response = result[0]
        assert response['id'] == request['data'][0]['id']

    def test_relationship_keys_get_inflected(self, post):
        class PostSchema(Schema):
            id = fields.Int()
            post_title = fields.Str(attribute='title')

            post_comments = fields.Relationship(
                'http://test.test/posts/{id}/comments/',
                related_url_kwargs={'id': '<id>'},
                attribute='comments'
            )

            class Meta:
                type_ = 'posts'
                inflect = dasherize

        data, errs = PostSchema().dump(post)
        assert not errs
        assert 'post-title' in data['data']['attributes']
        assert 'post-comments' in data['data']['relationships']
        related_href = data['data']['relationships']['post-comments']['links']['related']
        assert related_href == 'http://test.test/posts/{}/comments/'.format(post.id)


class TestAutoSelfUrls:
    class AuthorAutoSelfLinkSchema(Schema):
        id = fields.Int(dump_only=True)
        first_name = fields.Str(required=True)
        last_name = fields.Str(required=True)
        password = fields.Str(load_only=True, validate=validate.Length(6))
        twitter = fields.Str()

        class Meta:
            type_ = 'people'
            self_url = '/authors/{id}'
            self_url_kwargs = {'id': '<id>'}
            self_url_many = '/authors/'

    def test_self_url_kwargs_requires_self_url(self, author):
        class InvalidSelfLinkSchema(Schema):
            id = fields.Int()

            class Meta:
                type_ = 'people'
                self_url_kwargs = {'id': '<id>'}

        with pytest.raises(ValueError):
            InvalidSelfLinkSchema().dump(author).data

    def test_self_link_single(self, author):
        data = self.AuthorAutoSelfLinkSchema().dump(author).data
        assert 'links' in data
        assert data['links']['self'] == '/authors/{}'.format(author.id)

    def test_self_link_many(self, authors):
        data = self.AuthorAutoSelfLinkSchema(many=True).dump(authors).data
        assert 'links' in data
        assert data['links']['self'] == '/authors/'

        assert 'links' in data['data'][0]
        assert data['data'][0]['links']['self'] == '/authors/{}'.format(authors[0].id)

    def test_without_self_link(self, comments):
        data = CommentSchema(many=True).dump(comments).data

        assert 'data' in data
        assert type(data['data']) is list

        first = data['data'][0]
        assert first['id'] == comments[0].id
        assert first['type'] == 'comments'

        assert 'links' not in data


class ArticleSchema(Schema):
    id = fields.Integer()
    body = fields.String()
    author = fields.Relationship(
        dump_only=False, include_resource_linkage=True, many=False, type_='people')
    comments = fields.Relationship(
        dump_only=False, include_resource_linkage=True, many=True, type_='comments')

    class Meta:
        type_ = 'articles'


class PolygonSchema(Schema):
    id = fields.Integer(as_string=True)
    sides = fields.Integer()
    regular = fields.Boolean()
    # This is an attribute that uses the 'meta' key: /data/attributes/meta
    meta = fields.String()
    # This is the resource object's meta object: /data/meta
    resource_meta = fields.Meta()

    class Meta:
        type_ = 'shapes'


class TestMeta(object):

    serialized_shape = {
        'data': {
            'id': '1',
            'type': 'shapes',
            'attributes': {
                'sides': 3,
                'regular': False,
                'meta': 'This is an ill-advised (albeit valid) attribute name.',
            },
            'meta': {
                'some': 'metadata',
            },
        },
    }

    shape = {
        'id': 1,
        'sides': 3,
        'regular': False,
        'meta': 'This is an ill-advised (albeit valid) attribute name.',
        'resource_meta': {'some': 'metadata'},
    }

    def test_deserialize_meta(self):
        data = PolygonSchema().load(self.serialized_shape).data
        assert data
        assert data['id'] == 1
        assert data['sides'] == 3
        assert data['regular'] is False
        assert data['meta'] == \
               'This is an ill-advised (albeit valid) attribute name.'
        assert data['resource_meta'] == {'some': 'metadata'}

    def test_serialize_meta(self):
        data = PolygonSchema().dump(self.shape).data
        assert data == self.serialized_shape


class TestRelationshipLoading(object):

    article = {
        'data': {
            "id": "1",
            "type": "articles",
            "attributes": {
                "body": "Test"
            },
            "relationships": {
                'author': {
                    "data": {"type": "people", "id": "1"}
                },
                'comments': {
                    "data": [{"type": "comments", "id": "1"}]
                }
            }
        }
    }

    def _assert_relationship_error(self, pointer, errors):
        """Walk through the dictionary and determine if a specific
        relationship pointer exists
        """
        pointer = '/data/relationships/{}/data'.format(pointer)
        for error in errors:
            if pointer == error['source']['pointer']:
                return True
        return False

    def test_deserializing_relationship_fields(self):
        data = ArticleSchema().load(self.article).data
        assert data['body'] == "Test"
        assert data['author'] == "1"
        assert data['comments'] == ["1"]

    def test_deserializing_relationship_errors(self):
        data = self.article
        data['data']['relationships']['author']['data'] = {}
        data['data']['relationships']['comments']['data'] = [{}]
        result, errors = ArticleSchema().load(data)

        assert \
            self._assert_relationship_error('author', errors['errors']) is True
        assert \
            self._assert_relationship_error('comments', errors['errors']) is \
            True
