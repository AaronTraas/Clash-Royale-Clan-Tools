Building crtools
================

To build crtools, you will need:

- python 3.6+
- pip3
- GNU make

Your Python environment should be properly configured. Here's a sample from my
`.bash_profile`:

```
export PATH=/usr/local/opt/python3/libexec/bin:$PATH
export PATH=/usr/local/Cellar/python/3.7.3/Frameworks/Python.framework/Versions/3.7/bin:$PATH
export PYTHONPATH="/usr/local/lib/python3.7/site-packages:$PYTHONPATH"
```

To set up your dev environment, go to the repository root directory and type:

```
make develop
```

Then you should be able to just update the Python code in /src, and run
`crtools` on the command line as normal.

To do a regular install:

```
make install
```

To update crtools.pot with new strings from the Python source:

```
make translate-update
```

To build the .mo files for each locale:

```
make translate
```

To run the unit tests:

```
make test
```

To generate HTML coverage report in /htmlcov:

```
make coverage-html
```