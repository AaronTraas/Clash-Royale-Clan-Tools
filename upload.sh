#!/usr/bin/env bash

sudo python3 setup.py clean
sudo python3 setup.py sdist bdist_wheel
twine upload dist/*
