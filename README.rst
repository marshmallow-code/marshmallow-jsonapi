*******************
marshmallow-jsonapi
*******************

.. image:: https://badge.fury.io/py/marshmallow-jsonapi.svg
    :target: http://badge.fury.io/py/marshmallow-jsonapi
    :alt: Latest version

.. image:: https://travis-ci.org/marshmallow-code/marshmallow-jsonapi.svg
    :target: https://travis-ci.org/marshmallow-code/marshmallow-jsonapi
    :alt: Travis-CI

Homepage: http://marshmallow-jsonapi.readthedocs.io/

JSON API 1.0 (`https://jsonapi.org <http://jsonapi.org/>`_) formatting with `marshmallow <https://marshmallow.readthedocs.io>`_.

marshmallow-jsonapi provides a simple way to produce JSON API-compliant data in any Python web framework.

.. code-block:: python

    from marshmallow_jsonapi import Schema, fields

    class PostSchema(Schema):
        id = fields.Str(dump_only=True)
        title = fields.Str()

        author = fields.Relationship(
            '/authors/{author_id}',
            related_url_kwargs={'author_id': '<author.id>'},
        )

        comments = fields.Relationship(
            '/posts/{post_id}/comments',
            related_url_kwargs={'post_id': '<id>'},
            # Include resource linkage
            many=True, include_resource_linkage=True,
            type_='comments'
        )

        class Meta:
            type_ = 'posts'
            strict = True

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

Installation
============
::

    pip install marshmallow-jsonapi


Documentation
=============

Full documentation is available at https://marshmallow-jsonapi.readthedocs.io/.

Requirements
============

- Python >= 2.7 or >= 3.4

Project Links
=============

- Docs: http://marshmallow-jsonapi.readthedocs.io/
- Changelog: http://marshmallow-jsonapi.readthedocs.io/en/latest/changelog.html
- PyPI: https://pypi.python.org/pypi/marshmallow-jsonapi
- Issues: https://github.com/marshmallow-code/marshmallow-jsonapi/issues

Contributing
============

- Fork this repository
- Clone your fork to your computer
- Install dev requirements
- Create branch for your work
- Write a test for your work
- Implement your feature/fix and iterate until your test passes and the feature is complete
- Push to your fork and submit a pull request

License
=======

MIT licensed. See the bundled `LICENSE <https://github.com/marshmallow-code/marshmallow-jsonapi/blob/master/LICENSE>`_ file for more details.
