#!/bin/bash

SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")"; cd ..; pwd)
export PYTHONPATH=$SCRIPT_PATH:$PYTHONPATH
