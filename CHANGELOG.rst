*********
Changelog
*********

0.4.0 (2015-12-06)
==================

- Correctly serialize null and empty relationships (:issue:`10`). Thanks :user:`jo-tham` for the PR.
- Add ``self_url``, ``self_url_kwargs``, and ``self_url_many`` class Meta options for adding ``self`` links. Thanks :user:`asteinlein` for the PR.

0.3.0 (2015-10-18)
==================

* *Backwards-incompatible*: Replace ``HyperlinkRelated`` with ``Relationship`` field. Supports related links (``related``), relationship links (``self``), and resource linkages.
* *Backwards-incompatible*: Validate and deserialize JSON API-formatted request payloads.
* Fix error formatting when ``many=True``.
* Fix error formatting in strict mode.

0.2.2 (2015-09-26)
==================

* Fix for marshmallow 2.0.0 compat.

0.2.1 (2015-09-16)
==================

* Compatibility with marshmallow>=2.0.0rc2.

0.2.0 (2015-09-13)
==================

Features:

* Add framework-independent ``HyperlinkRelated`` field.
* Support inflection of attribute names via the ``inflect`` class Meta option.

Bug fixes:

* Fix for making ``HyperlinkRelated`` read-only by defualt.

Support:

* Docs updates.
* Tested on Python 3.5.

0.1.0 (2015-09-12)
==================

* First PyPI release.
* Include Schema that serializes objects to resource objects.
* Flask-compatible HyperlinkRelate field for serializing relationships.
* Errors are formatted as JSON API errror objects.
