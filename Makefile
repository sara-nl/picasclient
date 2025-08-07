SHELL := /bin/bash
ROOT := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: nothing
nothing:

help:
	@echo "no help info"

all:
	echo hello world

build:
	@echo "building picasclient..."
	@python setup.py build

install:
	@echo "installing picasclient..."
	@pip install -e .

uninstall:
	@echo "uninstalling picasclient..."
	@pip uninstall -y picasclient

test:
	@echo "running tests..."
	@pytest tests

tutorial:
	@echo "running tutorial..."
	@cd examples && jupytext --to ipynb 00-environment-setup.py --output 00-environment-setup.ipynb

clean:
	@rm -fvr \#* *~ *.exe out build *.egg* dist
	@rm -fvr examples/*.out examples/*.err
	@find . -name __pycache__ -exec rm -fvr '{}' \;
