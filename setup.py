#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(name='picas',
      version='0.3.0',
      description='Python client using CouchDB as a token pool server.',
      author='Jan Bot,Joris Borgdorff,Lodewijk Nauta',
      author_email='helpdesk@surf.nl',
      url='https://github.com/sara-nl/picasclient',
      download_url='https://github.com/sara-nl/picasclient/tarball/0.3.0',
      packages=['picas'],
      install_requires=['couchdb', 'stopit'],
      license="MIT",
      extras_require={
          'test': ['flake8', 'pytest'],
      },
      classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        ]
      )
