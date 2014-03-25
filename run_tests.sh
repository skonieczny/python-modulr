#!/usr/bin/env sh

pip install -r test_requirements.txt
python setup.py nosetests --disable-docstring "$@"
