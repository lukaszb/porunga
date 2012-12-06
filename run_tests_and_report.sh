#!/bin/bash

echo "Running test suite with coverage report at the end"
echo -e "( would require coverage python package to be installed )\n"

OMIT="porunga/utils/compat.py,porunga/tests/__init__.py"
coverage run setup.py test
coverage report -m --include "porunga/*" --omit $OMIT
