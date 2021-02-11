# pybgen - Module to process BGEN files

[![Build Status](https://travis-ci.com/lemieuxl/pybgen.svg?branch=master)](https://travis-ci.com/lemieuxl/pybgen)
[![Coverage Status](https://coveralls.io/repos/github/lemieuxl/pybgen/badge.svg?branch=master)](https://coveralls.io/github/lemieuxl/pybgen?branch=master)
[![PyPI version](https://badge.fury.io/py/pybgen.svg)](http://badge.fury.io/py/pybgen)

`PyBGEN` is a Python module to read and write BGEN binary files and extract
dosage data.

A short documentation is available at
[https://lemieuxl.github.io/pybgen/](https://lemieuxl.github.io/pybgen/).

## Dependencies

The tool requires a standard [Python](http://python.org/) installation (2.7 and
3.6 or higher are supported) with the following modules:

1. [numpy](http://www.numpy.org/) version 1.12.0 or latest
2. [six](https://pythonhosted.org/six/) version 1.10.0 or latest

The tool has been tested on *Linux*, but should work on *MacOS* and *Windows*
operating systems as well.

## Installation

Using `pip`:

```bash
pip install pybgen
```

Using `conda`:

```bash
conda install pybgen -c http://statgen.org/wp-content/uploads/Softwares/pybgen
```

It is possible to add the channel to conda's configuration, so that the
`-c http://statgen.org/...` can be omitted to update or install the package.
To add the channel, perform the following command:

```bash
conda config --add channels http://statgen.org/wp-content/uploads/Softwares/pybgen
```

### Updating

To update the module using `pip`:

```bash
pip install -U pybgen
```

To update the module using `conda`:

```bash
# If the channel has been configured (see above)
conda update pybgen

# Otherwise
conda update pybgen -c http://statgen.org/wp-content/uploads/Softwares/pybgen
```

## Testing

To test the module, just perform the following command:

```console
$ python -m pybgen.tests
......................................................................
......................................................................
......................................................................
......................................................................
......................................................................
......................................................................
......................................................................
......................................
----------------------------------------------------------------------
Ran 528 tests in 13.171s

OK
```
