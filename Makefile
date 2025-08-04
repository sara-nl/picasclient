SHELL := /bin/bash
ROOT := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: nothing
nothing:

help:
	@echo "no help info"

all:
	echo hello world

clean:
	rm -fvr \#* *~ *.exe out build
	find . -name __pycache__ -exec rm -fvr '{}' \;
