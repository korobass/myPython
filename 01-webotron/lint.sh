#!/bin/bash

PACKAGE=webotron
pycodestyle $PACKAGE
pydocstyle $PACKAGE
pylint $PACKAGE
pyflakes $PACKAGE