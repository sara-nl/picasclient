import sys
import pathlib
from setuptools import setup, find_packages

setup_cwd = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(setup_cwd))
from picas import metadata

# Debug: Print what packages are found
packages = find_packages()
print(f"Found packages: {packages}")

# Debug: Check if the entry point module exists
entry_point_check = pathlib.Path(setup_cwd) / 'picas' / 'apps' / 'picas_cli.py'
print(f"Entry point file exists: {entry_point_check.exists()} at {entry_point_check}")

setup(
    name=metadata.package,
    version=metadata.version,
    description=metadata.description,
    author=metadata.authors,
    author_email=metadata.emails,
    url=metadata.url,
    packages=packages,
    entry_points={
        'console_scripts': [
            'picas-cli=picas.apps.picas_cli:main'
        ],
    },
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=[],
)
