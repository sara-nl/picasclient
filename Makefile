SHELL := /bin/bash
ROOT := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: nothing
nothing:

help:
	@echo "no help info"

all:
	echo hello world

build:
	@echo "Building picasclient..."
	@python setup.py build

install:
	@echo "Installing picasclient..."
	@pip install -e .

uninstall:
	@echo "Uninstalling picasclient..."
	@pip uninstall -y picasclient

test:
	@echo "Running tests..."
	@pytest tests

clean:
	rm -fvr \#* *~ *.exe out build
	find . -name __pycache__ -exec rm -fvr '{}' \;
