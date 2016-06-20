# -*- coding: utf-8 -*-
import os
import sys
import webbrowser

from invoke import task, run

docs_dir = 'docs'
build_dir = os.path.join(docs_dir, '_build')

@task
def test(ctx):
    flake(ctx)
    import pytest
    errcode = pytest.main(['tests'])
    sys.exit(errcode)

@task
def flake(ctx):
    """Run flake8 on codebase."""
    run('flake8 .', echo=True)

@task
def watch(ctx):
    """Run tests when a file changes. Requires pytest-xdist."""
    import pytest
    errcode = pytest.main(['-f'])
    sys.exit(errcode)

@task
def clean(ctx):
    run("rm -rf build")
    run("rm -rf dist")
    run("rm -rf marshmallow-jsonapi.egg-info")
    clean_docs(ctx)
    print("Cleaned up.")

@task
def clean_docs(ctx):
    run("rm -rf %s" % build_dir, echo=True)

@task
def browse_docs(ctx):
    path = os.path.join(build_dir, 'index.html')
    webbrowser.open_new_tab(path)

@task
def docs(ctx, clean=False, browse=False, watch=False):
    """Build the docs."""
    if clean:
        clean_docs(ctx)
    run("sphinx-build %s %s" % (docs_dir, build_dir), echo=True)
    if browse:
        browse_docs(ctx)
    if watch:
        watch_docs(ctx)

@task
def watch_docs(ctx):
    """Run build the docs when a file changes."""
    try:
        import sphinx_autobuild  # noqa
    except ImportError:
        print('ERROR: watch task requires the sphinx_autobuild package.')
        print('Install it with:')
        print('    pip install sphinx-autobuild')
        sys.exit(1)
    docs()
    run('sphinx-autobuild {} {}'.format(docs_dir, build_dir), pty=True)

@task
def readme(ctx, browse=False):
    run("rst2html.py README.rst > README.html", echo=True)
    if browse:
        webbrowser.open_new_tab('README.html')

@task
def publish(ctx, test=False):
    """Publish to the cheeseshop."""
    clean(ctx)
    try:
        __import__('wheel')
    except ImportError:
        print('wheel required. Run `pip install wheel`.')
        sys.exit(1)
    if test:
        run('python setup.py register -r test sdist bdist_wheel', echo=True)
        run('twine upload dist/* -r test', echo=True)
    else:
        run('python setup.py register sdist bdist_wheel', echo=True)
        run('twine upload dist/*', echo=True)
