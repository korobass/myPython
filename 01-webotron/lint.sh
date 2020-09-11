#!/bin/bash
pipenv install pycodestyle pydocstyle pylint pyflakes
PACKAGE=webotron
pipenv run pycodestyle $PACKAGE
pipenv run pydocstyle $PACKAGE
pipenv run pylint $PACKAGE
pipenv run pyflakes $PACKAGE