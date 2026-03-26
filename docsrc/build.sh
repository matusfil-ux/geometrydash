#!/usr/bin/env bash

# error may be thrown if environment variable "LC_ALL" is not set to value "C"
export LC_ALL=C

# remove old docs directory if it exists
rm -rfd docs && mkdir docs

# create new docs directory
sphinx-build docsrc docs
