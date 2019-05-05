# -*- coding: utf-8 -*-
import re
from setuptools import setup, find_packages

INSTALL_REQUIRES = (
    'marshmallow>=2.8.0',
)
EXTRAS_REQUIRE = {
    'tests': [
        'pytest',
        'mock',
        'faker==1.0.5',
        'Flask==1.0.2',
    ],
    'lint': [
        'flake8==3.7.7',
        'pre-commit==1.16.0',
    ],
}
EXTRAS_REQUIRE['dev'] = (
    EXTRAS_REQUIRE['tests'] +
    EXTRAS_REQUIRE['lint'] +
    ['tox']
)


def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version


__version__ = find_version('marshmallow_jsonapi/__init__.py')


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


setup(
    name='marshmallow-jsonapi',
    version=__version__,
    description='JSON API 1.0 (https://jsonapi.org) formatting with marshmallow',
    long_description=read('README.rst'),
    author='Steven Loria',
    author_email='sloria1@gmail.com',
    url='https://github.com/marshmallow-code/marshmallow-jsonapi',
    packages=find_packages(exclude=('test*', )),
    package_dir={'marshmallow-jsonapi': 'marshmallow-jsonapi'},
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    license='MIT',
    zip_safe=False,
    keywords=(
        'marshmallow-jsonapi marshmallow marshalling serialization '
        'jsonapi deserialization validation'
    ),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    project_urls={
        'Bug Reports': 'https://github.com/marshmallow-code/marshmallow-jsonapi/issues',
        'Funding': 'https://opencollective.com/marshmallow',
    },
)
