# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
import re

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# single-sourcing the version
with open(path.join(here, 'crtools/_version.py')) as f:
    exec(f.read())

setup(
    name='crtools',

    # Version single-sourced from crtools/_version.py
    version=__version__,

    description='Python tools for creating a clan management dashboard for Clash Royale',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/AaronTraas/Clash-Royale-Clan-Tools',

    # Author details
    author='Aaron Traas',
    author_email='aaron@traas.org',

    # Choose your license
    license='LGPLv3+',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python :: 3',
    ],

    # What does your project relate to?
    keywords='ClashRoyale',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    setup_requires=['babel'],
    install_requires=['jinja2','configparser','pyroyale', 'requests'],
    tests_requires=['pytest','pytest-runner','coverage','requests_mock'],

    include_package_data=True,

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    #extras_require={
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    #package_data={
    #    'sample': ['package_data.dat'],
    #},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'crtools=crtools:main',
        ],
    },
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/AaronTraas/Clash-Royale-Clan-Tools/issues',
        'Source': 'https://github.com/AaronTraas/Clash-Royale-Clan-Tools',
    },
)
