*******************
marshmallow-jsonapi
*******************

.. image:: https://badgen.net/pypi/v/marshmallow-jsonapi
    :target: https://pypi.org/project/marshmallow-jsonapi/
    :alt: PyPI version

.. image:: https://dev.azure.com/sloria/sloria/_apis/build/status/marshmallow-code.marshmallow-jsonapi?branchName=dev
    :target: https://dev.azure.com/sloria/sloria/_build/latest?definitionId=7&branchName=dev
    :alt: Build status

.. image:: https://readthedocs.org/projects/marshmallow-jsonapi/badge/
   :target: https://marshmallow-jsonapi.readthedocs.io/
   :alt: Documentation

.. image:: https://badgen.net/badge/marshmallow/3
    :target: https://marshmallow.readthedocs.io/en/latest/upgrading.html
    :alt: marshmallow 3 compatible

.. image:: https://badgen.net/badge/code%20style/black/000
    :target: https://github.com/ambv/black
    :alt: code style: black

Homepage: http://marshmallow-jsonapi.readthedocs.io/

JSON API 1.0 (`https://jsonapi.org <http://jsonapi.org/>`_) formatting with `marshmallow <https://marshmallow.readthedocs.io>`_.

marshmallow-jsonapi provides a simple way to produce JSON API-compliant data in any Python web framework.

.. code-block:: python

    from marshmallow_jsonapi import Schema, fields


    class PostSchema(Schema):
        id = fields.Str(dump_only=True)
        title = fields.Str()

        author = fields.Relationship(
            "/authors/{author_id}", related_url_kwargs={"author_id": "<author.id>"}
        )

        comments = fields.Relationship(
            "/posts/{post_id}/comments",
            related_url_kwargs={"post_id": "<id>"},
            # Include resource linkage
            many=True,
            include_resource_linkage=True,
            type_="comments",
        )

        class Meta:
            type_ = "posts"


    post_schema = PostSchema()
    post_schema.dump(post)
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

- Python >= 3.6

Project Links
=============

- Docs: http://marshmallow-jsonapi.readthedocs.io/
- Changelog: http://marshmallow-jsonapi.readthedocs.io/en/latest/changelog.html
- Contributing Guidelines: https://marshmallow-jsonapi.readthedocs.io/en/latest/contributing.html
- PyPI: https://pypi.python.org/pypi/marshmallow-jsonapi
- Issues: https://github.com/marshmallow-code/marshmallow-jsonapi/issues

License
=======

MIT licensed. See the bundled `LICENSE <https://github.com/marshmallow-code/marshmallow-jsonapi/blob/master/LICENSE>`_ file for more details.
