*******************
marshmallow-jsonapi
*******************

.. image:: https://img.shields.io/pypi/v/marshmallow-jsonapi.svg
    :target: https://pypi.python.org/pypi/marshmallow-jsonapi
    :alt: Latest version

.. image:: https://img.shields.io/travis/marshmallow-code/marshmallow-jsonapi.svg
    :target: https://travis-ci.org/marshmallow-code/marshmallow-jsonapi
    :alt: Travis-CI

Homepage: http://marshmallow-jsonapi.rtfd.org/

JSON API 1.0 (`https://jsonapi.org <http://jsonapi.org/>`_) formatting with `marshmallow <https://marshmallow.readthedocs.org>`_.

marshmallow-jsonapi provides a simple way to produce JSON API-compliant data in any Python web framework.

.. code-block:: python

    from marshmallow_jsonapi import Schema, fields

    class PostSchema(Schema):
        id = fields.Str(dump_only=True)
        title = fields.Str()

        author = fields.HyperlinkRelated(
            '/authors/{author_id}',
            url_kwargs={'author_id': '<author.id>'},
        )

        comments = fields.HyperlinkRelated(
            '/posts/{post_id}/comments',
            url_kwargs={'post_id': '<id>'},
            # Include resource linkage
            many=True, include_data=True,
            type_='comments'
        )

        class Meta:
            type_ = 'posts'


    post_schema = PostSchema()
    post_schema.dump(post).data
    # {
    #     "data": {
    #         "id": "1",
    #         "type": "posts"
    #         "attributes": {
    #             "title": "JSON API paints my bikeshed!"
    #         },
    #         "relationships": {
    #             "author": {
    #                 "links": {
    #                     "related": "/authors/9"
    #                 }
    #             },
    #             "comments": {
    #                 "links": {
    #                     "related": "/posts/1/comments/"
    #                 }
    #                 "data": [
    #                     {"id": 5, "type": "comments"},
    #                     {"id": 12, "type": "comments"}
    #                 ],
    #             }
    #         },
    #     }
    # }


Error formatting
================

``Schema.load`` and ``Schema.validate`` will return JSON API-formatted `Error objects <http://jsonapi.org/format/#error-objects>`_.

.. code-block:: python

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

    schema = AuthorSchema()
    schema.validate({'first_name': 'Dan', 'password': 'short'})
    # {
    #     "errors": [
    #         {
    #             "detail": "Shorter than minimum length 6.",
    #             "source": {"pointer": "/data/attributes/password"}
    #         },
    #         {
    #             "detail": "Missing data for required field.",
    #             "source": {"pointer": "/data/attributes/last_name"}
    #         }
    #     ]
    # }


Inflection
==========

You can optionally specify a function to transform attribute names. For example, you may decide to follow JSON API's `recommendation <http://jsonapi.org/recommendations/#naming>`_ to use "dasherized" names.

.. code-block:: python

    from marshmallow_jsonapi import Schema, fields

    def dasherize(text):
        return text.replace('_', '-')

    class AuthorSchema(Schema):
        id = fields.Str(dump_only=True)
        first_name = fields.Str(required=True)
        last_name = fields.Str(required=True)

        class Meta:
            type_ = 'people'
            inflect = dasherize

    result = AuthorSchema().dump(author)
    result.data
    # {
    #     'data': {
    #         'id': '9',
    #         'type': 'people',
    #         'attributes': {
    #             'first-name': 'Dan',
    #             'last-name': 'Gebhardt'
    #         }
    #     }
    # }

Flask integration
=================

Marshmallow-jsonapi includes optional utilities to integrate with Flask.

For example, the ``HyperlinkRelated`` field in the ``marshmallow_jsonapi.flask`` module allows you to pass an endpoint name instead of a path template.

The above schema could be rewritten in a Flask application like so:

.. code-block:: python

    from marshmallow_jsonapi import Schema, fields
    from marshmallow_jsonapi.flask import HyperlinkRelated

    class PostSchema(Schema):
        id = fields.Str(dump_only=True)
        title = fields.Str()

        author = HyperlinkRelated(
            # Flask endpoint name, passed to url_for
            endpoint='author_detail',
            url_kwargs={'author_id': '<author.id>'},
        )

        comments = HyperlinkRelated(
            endpoint='posts_comments',
            url_kwargs={'post_id': '<id>'},
            # Include resource linkage
            many=True, include_data=True,
            type_='comments'
        )

        class Meta:
            type_ = 'posts'

See `here <https://github.com/marshmallow-code/marshmallow-jsonapi/blob/master/examples/flask_example.py>`_ for a full example.

Installation
============
::

    pip install marshmallow-jsonapi


Documentation
=============

Full documentation is available at https://marshmallow-jsonapi.readthedocs.org/.

Requirements
============

- Python >= 2.7 or >= 3.3

Project Links
=============

- Docs: http://marshmallow-jsonapi.rtfd.org/
- Changelog: http://marshmallow-jsonapi.readthedocs.org/en/latest/changelog.html
- PyPI: https://pypi.python.org/pypi/marshmallow-jsonapi
- Issues: https://github.com/marshmallow-code/marshmallow-jsonapi/issues


License
=======

MIT licensed. See the bundled `LICENSE <https://github.com/marshmallow-code/marshmallow-jsonapi/blob/master/LICENSE>`_ file for more details.
