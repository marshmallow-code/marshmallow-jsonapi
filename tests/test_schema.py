#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from marshmallow import validate, ValidationError
from marshmallow_jsonapi import Schema, fields
from marshmallow_jsonapi.exceptions import IncorrectTypeError

class AuthorSchema(Schema):
    id = fields.Int(dump_only=True)
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
            AuthorSchema().validate(author)
        assert excinfo.value.args[0] == '`data` object must include `type` key.'

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
                    'pointer': '/data/type'
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
