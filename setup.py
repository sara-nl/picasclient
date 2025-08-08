import os
import sys
import pathlib
import shutil
from setuptools import setup, find_packages

setup_cwd = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, os.path.join(setup_cwd, '.'))
from picas import metadata

setup(
    name=metadata.package,
    version=metadata.version,
    description=metadata.description,
    author=metadata.authors,
    author_email=metadata.emails,
    url=metadata.url,
    packages=find_packages(where='.', include=['picas', 'picas.*']),
    package_dir={'picas': 'picas'},
    entry_points={
        'console_scripts': [
            'picas-cli=picas.apps.picas:main'
        ],
    }
)
