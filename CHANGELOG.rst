*********
Changelog
*********

0.22.0 (2019-09-15)
===================

Deprecation/Removals:

* Drop support for Python 2.7 and 3.6.
  Only Python>=3.6 is supported (:issue:`251`).
* Drop support for marshmallow 3 pre-releases. Only stable versions >=2.15.2 are supported.
* Remove ``fields.Meta``.

Bug fixes:

* Address ``DeprecationWarning`` raised by ``Field.fail`` on marshmallow 3.

0.21.2 (2019-07-01)
===================

Bug fixes:

* marshmallow 3.0.0rc7 compatibility (:pr:`233`).

Other changes:

* Format with pyupgrade and black (:pr:`235`).
* Switch to Azure Pipelines for CI (:pr:`234`).

0.21.1 (2019-05-05)
===================

Bug fixes:

* marshmallow 3.0.0rc6 cmpatibility (:pr:`221`).

0.21.0 (2018-12-16)
===================

Bug fixes:

* *Backwards-incompatible*: Revert URL quoting introduced in 0.20.2
  (:issue:`184`). If you need quoting, override `Schema.generate_url`.

.. code-block:: python

  from marshmallow_jsonapi import Schema
  from werkzeug.urls import url_fix


  class MySchema(Schema):
      def generate_url(self, link, **kwargs):
          url = super().generate_url(link, **kwargs)
          return url_fix(url)

Thanks :user:`kgutwin` for reporting the issue.

* Fix `Relationship` deserialization behavior when ``required=False`` (:issue:`177`).
  Thanks :user:`aberres` for reporting and :user:`scottwernervt` for the
  fix.

Other changes:

* Test against Python 3.7.

0.20.5 (2018-10-27)
===================

Bug fixes:

* Fix deserializing ``id`` field to non-string types (:pr:`179`).
  Thanks :user:`aberres` for the catch and patch.

0.20.4 (2018-10-04)
===================

Bug fixes:

* Fix bug where multi-level nested relationships would not be properly
  deserialized (:issue:`127`). Thanks :user:`ww3pl` for the catch and
  patch.

0.20.3 (2018-09-13)
===================

Bug fixes:

* Fix missing load validation when data is not a collection
  but many=True (:pr:`161`). Thanks :user:`grantHarris`.

0.20.2 (2018-08-15)
===================

Bug fixes:

* Fix issues where generated URLs are unquoted (:pr:`147`). Thanks
  :user:`grantHarris`.

Other changes:

* Fix tests against marshmallow 3.0.0b13.

0.20.1 (2018-07-15)
===================

Bug fixes:

* Fix deserializing ``missing`` with a `Relationship` field (:issue:`130`).
  Thanks :user:`kumy` for the catch and patch.

0.20.0 (2018-06-10)
===================

Bug fixes:

* Fix serialization of ``id`` for ``Relationship`` fields when
  ``attribute`` is set (:issue:`69`). Thanks :user:`jordal` for
  reporting and thanks :user:`scottwernervt` for the fix.

Note: The above fix could break some code that set
``Relationship.id_field`` before instantiating it.
Set ``Relationship.default_id_field`` instead.

.. code-block:: python


    # before
    fields.Relationship.id_field = "item_id"

    # after
    fields.Relationship.default_id_field = "item_id"


Support:

* Test refactoring and various doc improvements (:issue:`63`, :issue:`86`,
  :issue:`121,` and :issue:`122`). Thanks :user:`scottwernervt`.

0.19.0 (2018-05-27)
===================

Features:

* Schemas passed to ``fields.Relationship`` will inherit context from
  the parent schema (:issue:`84`). Thanks :user:`asteinlein` and
  :user:`scottwernervt` for the PRs.

0.18.0 (2018-05-19)
===================

Features:

* Add ``fields.ResourceMeta`` for serializing a resource-level meta
  object (:issue:`107`). Thanks :user:`scottwernervt`.

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
