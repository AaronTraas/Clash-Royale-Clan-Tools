#!/usr/bin/env bash

sudo rm -rf dist build
sudo python3 setup.py sdist bdist_wheel
twine upload dist/*
