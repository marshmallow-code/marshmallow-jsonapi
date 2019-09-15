Contributing Guidelines
=======================

Questions, Feature Requests, Bug Reports, and Feedback…
-------------------------------------------------------

…should all be reported on the `Github Issue Tracker`_ .

.. _`Github Issue Tracker`: https://github.com/marshmallow-code/marshmallow-jsonapi/issues?state=open

Setting Up for Local Development
--------------------------------

1. Fork marshmallow-jsonapi_ on Github.

::

    $ git clone https://github.com/marshmallow-code/marshmallow-jsonapi.git
    $ cd marshmallow-jsonapi

2. Install development requirements. **It is highly recommended that you use a virtualenv.**
   Use the following command to install an editable version of
   marshmallow-jsonapi along with its development requirements.

::

    # After activating your virtualenv
    $ pip install -e '.[dev]'

3. Install the pre-commit hooks, which will format and lint your git staged files.

::

    # The pre-commit CLI was installed above
    $ pre-commit install

Git Branch Structure
--------------------

Marshmallow abides by the following branching model:


``dev``
    Current development branch. **New features should branch off here**.

``X.Y-line``
    Maintenance branch for release ``X.Y``. **Bug fixes should be sent to the most recent release branch.** The maintainer will forward-port the fix to ``dev``. Note: exceptions may be made for bug fixes that introduce large code changes.

**Always make a new branch for your work**, no matter how small. Also, **do not put unrelated changes in the same branch or pull request**. This makes it more difficult to merge your changes.

Pull Requests
--------------

1. Create a new local branch.
::

    $ git checkout -b name-of-feature dev

2. Commit your changes. Write `good commit messages <http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>`_.
::

    $ git commit -m "Detailed commit message"
    $ git push origin name-of-feature

3. Before submitting a pull request, check the following:

- If the pull request adds functionality, it is tested and the docs are updated.
- You've added yourself to ``AUTHORS.rst``.

4. Submit a pull request to ``marshmallow-code:dev`` or the appropriate maintenance branch. The `CI <https://dev.azure.com/sloria/sloria/_build/latest?definitionId=7&branchName=dev>`_ build must be passing before your pull request is merged.

Running tests
-------------

To run all To run all tests: ::

    $ pytest

To run syntax checks: ::

    $ tox -e lint

(Optional) To run tests in all supported Python versions in their own virtual environments (must have each interpreter installed): ::

    $ tox

Documentation
-------------

Contributions to the documentation are welcome. Documentation is written in `reStructured Text`_ (rST). A quick rST reference can be found `here <http://docutils.sourceforge.net/docs/user/rst/quickref.html>`_. Builds are powered by Sphinx_.

To build the docs in "watch" mode: ::

   $ tox -e watch-docs

Changes in the `docs/` directory will automatically trigger a rebuild.

.. _Sphinx: http://sphinx.pocoo.org/
.. _`reStructured Text`: http://docutils.sourceforge.net/rst.html
.. _marshmallow-jsonapi: https://github.com/marshmallow-code/marshmallow-jsonapi
