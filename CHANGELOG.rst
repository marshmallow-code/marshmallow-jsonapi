*********
Changelog
*********

0.18.0 (2018-05-19)
===================

Features:

* Add ``fields.ResourceMeta`` for serializing a resource-level meta
  object (:issue:``). Thanks :user:`scottwernervt`.

Other changes:

* *Backwards-incompatible*: Drop official support for Python 3.4.

0.17.0 (2018-04-29)
===================

Features:

* Add support for marshmallow 3 (:issue:`97`). Thanks :user:`rockmnew`.
* Thanks :user:`mdodsworth` for helping with :issue:`101`.
* Move meta information object to document top level (:issue:`95`). Thanks :user:`scottwernervt`.

0.16.0 (2017-11-08)
===================

Features:

* Add support for exluding or including nested fields on relationships
  (:issue:`94`). Thanks :user:`scottwernervt` for the PR.

Other changes:

* *Backwards-incompatible*: Drop support for marshmallow<2.8.0

0.15.1 (2017-08-23)
===================

Bug fixes:

* Fix pointer for ``id`` in error objects (:issue:`90`). Thanks
  :user:`rgant` for the catch and patch.

0.15.0 (2017-06-27)
===================

Features:

* ``Relationship`` field supports deserializing included data
  (:issue:`83`). Thanks :user:`anuragagarwal561994` for the suggestion
  and thanks :user:`asteinlein` for the PR.

0.14.0 (2017-04-30)
===================

Features:

* ``Relationship`` respects its passed ``Schema's`` ``get_attribute`` method when getting the ``id`` field for resource linkages (:issue:`80`). Thanks :user:`scmmmh` for the PR.

0.13.0 (2017-04-18)
===================

Features:

* Add support for including deeply nested relationships in compount documents (:issue:`61`). Thanks :user:`mrhanky17` for the PR.

0.12.0 (2017-04-16)
===================

Features:

* Use default attribute value instead of raising exception if relationship is ``None`` on ``Relationship`` field (:issue:`75`). Thanks :user:`akira-dev`.

0.11.1 (2017-04-06)
===================

Bug fixes:

- Fix formatting JSON pointer when serializing an invalid object at index 0 (:issue:`77`). Thanks :user:`danpoland` for the catch and patch.

0.11.0 (2017-03-12)
===================

Bug fixes:

* Fix compatibility with marshmallow 3.x.


Other changes:

* *Backwards-incompatible*: Remove unused `utils.get_value_or_raise` function.

0.10.2 (2017-03-08)
===================

Bug fixes:

* Fix format of error object returned when ``data`` key is not included in input (:issue:`66`). Thanks :user:`RazerM`.
* Fix serializing compound documents when ``Relationship`` is passed a schema class and ``many=True`` (:issue:`67`). Thanks :user:`danpoland` for the catch and patch.

0.10.1 (2017-02-05)
===================

Bug fixes:

* Serialize ``None`` and empty lists (``[]``) to valid JSON-API objects (:issue:`58`). Thanks :user:`rgant` for reporting and sending a PR.

0.10.0 (2017-01-05)
===================

Features:

* Add ``fields.Meta`` for (de)serializing ``meta`` data on resource objects (:issue:`28`). Thanks :user:`rubdos` for the suggestion and initial work. Thanks :user:`RazerM` for the PR.

Other changes:

* Test against Python 3.6.

0.9.0 (2016-10-08)
==================

Features:

* Add Flask-specific schema with class Meta options for self link generation: ``self_view``, ``self_view_kwargs``, and ``self_view_many`` (:issue:`51`). Thanks :user:`asteinlein`.

Bug fixes:

* Fix formatting of validation error messages on newer versions of marshmallow.

Other changes:

* Drop official support for Python 3.3.

0.8.0 (2016-06-20)
==================

Features:

* Add support for compound documents (:issue:`11`). Thanks :user:`Tim-Erwin` and :user:`woodb` for implementing this.
* *Backwards-incompatible*: Remove ``include_data`` parameter from ``Relationship``. Use ``include_resource_linkage`` instead.

0.7.1 (2016-05-08)
==================

Bug fixes:

* Format correction for error objects (:issue:`47`). Thanks :user:`ZeeD26` for the PR.

0.7.0 (2016-04-03)
==================

Features:

* Correctly format ``messages`` attribute of ``ValidationError`` raised when ``type`` key is missing in input (:issue:`43`). Thanks :user:`ZeeD26` for the catch and patch.
* JSON pointers for error objects for relationships will point to the ``data`` key (:issue:`41`). Thanks :user:`cmanallen` for the PR.

0.6.0 (2016-03-24)
==================

Features:

* ``Relationship`` deserialization improvements: properly validate to-one and to-many relatinoships and validate the presense of the ``data`` key (:issue:`37`). Thanks :user:`cmanallen` for the PR.
* ``attributes`` is no longer a required key in the ``data`` object (:issue:`#39`, :issue:`42`). Thanks :user:`ZeeD26` for reporting and :user:`cmanallen` for the PR.
* Added ``id`` serialization (:issue:`39`). Thanks again :user:`cmanallen`.

0.5.0 (2016-02-08)
==================

Features:

* Add relationship deserialization (:issue:`15`).
* Allow serialization of foreign key attributes (:issue:`32`).
* Relationship IDs serialize to strings, as is required by JSON-API (:issue:`31`).
* ``Relationship`` field respects ``dump_to`` parameter (:issue:`33`).

Thanks :user:`cmanallen` for all of these changes.

Other changes:

* The minimum supported marshmallow version is 2.3.0.

0.4.2 (2015-12-21)
==================

Bug fixes:

* Relationship names are inflected when appropriate (:issue:`22`). Thanks :user:`angelosarto` for reporting.

0.4.1 (2015-12-19)
==================

Bug fixes:

* Fix serializing null and empty relationships with ``flask.Relationship`` (:issue:`24`). Thanks :user:`floqqi` for the catch and patch.

0.4.0 (2015-12-06)
==================

* Correctly serialize null and empty relationships (:issue:`10`). Thanks :user:`jo-tham` for the PR.
* Add ``self_url``, ``self_url_kwargs``, and ``self_url_many`` class Meta options for adding ``self`` links. Thanks :user:`asteinlein` for the PR.

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
