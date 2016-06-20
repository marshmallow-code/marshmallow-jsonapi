*******************
marshmallow-jsonapi
*******************

Release v\ |version|. (:ref:`Changelog <changelog>`)

JSON API 1.0 (`https://jsonapi.org <http://jsonapi.org/>`_) formatting with `marshmallow <https://marshmallow.readthedocs.io>`_.

marshmallow-jsonapi provides a simple way to produce JSON API-compliant data in any Python web framework.

.. code-block:: python

    from marshmallow_jsonapi import Schema, fields

    class PostSchema(Schema):
        id = fields.Str(dump_only=True)
        title = fields.Str()

        author = fields.Relationship(
            related_url='/authors/{author_id}',
            related_url_kwargs={'author_id': '<author.id>'},
        )

        comments = fields.Relationship(
            related_url='/posts/{post_id}/comments',
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

Guide
=====

.. toctree::
    :maxdepth: 2

    quickstart

API Reference
=============

.. toctree::
   :maxdepth: 2

   api_reference

Project info
============

.. toctree::
   :maxdepth: 1

   changelog
   authors
   contributing
   license

Links
=====

- `marshmallow-jsonapi @ GitHub <https://github.com/marshmallow-code/marshmallow-jsonapi>`_
- `marshmallow-jsonapi @ PyPI <https://pypi.python.org/pypi/marshmallow-jsonapi>`_
- `Issue Tracker <https://github.com/marshmallow-code/marshmallow-jsonapi/issues>`_
