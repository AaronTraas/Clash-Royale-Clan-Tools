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
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python :: 3',
    ],

    keywords='ClashRoyale',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    setup_requires=['babel'],
    install_requires=['jinja2','configparser','pyroyale>=1.0.3', 'requests', 'discord-webhook', 'google-api-python-client'],

    include_package_data=True,

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
