# Define required macros here
SHELL = /bin/sh

SRCDIR = ./pyroyale
TESTDIR = ./tests

clean:
	python3 setup.py clean
	rm -rf build dist .pytest_cache *.egg-info $(SRCDIR)/__pycache__ $(TESTDIR)/__pycache__ MANIFEST

install:
	python3 setup.py install

develop:
	python3 setup.py develop

test-depend:
	pip3 install coverage pytest pytest-runner

test: test-depend
	python3 setup.py test

coverage: test-depend
	coverage run setup.py test
	coverage xml

sonar: coverage
	sonar-scanner -Dsonar.projectVersion=`python -c "import sys; from crtools import __version__; sys.stdout.write(__version__)"`

translate:
	python setup.py extract_messages
	python setup.py compile_catalog

dist: translate
	python3 setup.py sdist bdist_wheel

upload: dist
	twine upload dist/*
