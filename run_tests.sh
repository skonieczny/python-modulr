#!/usr/bin/env bash

pip install -r test_requirements.txt
python setup.py nosetests --disable-docstring "$@"
