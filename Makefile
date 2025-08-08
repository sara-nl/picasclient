SHELL := /bin/bash
ROOT := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: nothing
nothing:

help:
	@echo "no help info"

all:
	echo hello world

build:
	@echo "building picas..."
	@python setup.py build

clean-build:
	@echo "cleaning build artifacts..."
	@rm -rf picas.egg-info picasclient.egg-info build dist
	@python -m pip uninstall -y picas || true

install: | build clean-build
	@echo "installing picasclient (editable)..."
	@rm -rf picas.egg-info
	@python -m pip install -e .

uninstall:
	@echo "uninstalling picasclient..."
	@python -m pip uninstall -y picas || true

test:
	@echo "running tests..."
	@pytest tests

tutorial:
	@echo "running tutorial..."
	@cd examples && jupytext --to ipynb 00-environment-setup.py --output 00-environment-setup.ipynb
	@cd examples && jupytext --to ipynb 01-database-setup.py --output 01-database-setup.ipynb

clean: clean-build
	@rm -fvr \#* *~ *.exe out build *.egg* dist
	@rm -fvr examples/*.out examples/*.err
	@find . -name __pycache__ -exec rm -fvr '{}' \;
