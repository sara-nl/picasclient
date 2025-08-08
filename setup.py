import sys
import pathlib
from setuptools import setup, find_packages

setup_cwd = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(setup_cwd))
from picas import metadata

setup(
    name=metadata.package,
    version=metadata.version,
    description=metadata.description,
    author=metadata.authors,
    author_email=metadata.emails,
    url=metadata.url,
    packages=find_packages(where='.'),
    package_dir={'': '.'},
    entry_points={
        'console_scripts': [
            'picas-cli=picas.apps.picas_cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=[],
)
