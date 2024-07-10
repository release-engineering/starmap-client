# StArMap Client

The client implementation for _StArMap_ service,
used by [release-engineering](https://github.com/release-engineering) publishing tools.

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/release-engineering/starmap-client/tox-test.yml)
![GitHub Release](https://img.shields.io/github/v/release/release-engineering/starmap-client)
[![PyPI version](https://badge.fury.io/py/starmap-client.svg)](https://badge.fury.io/py/starmap-client)

- [Source](https://github.com/release-engineering/starmap-client)
- [Documentation](https://release-engineering.github.io/starmap-client/)

## Overview

The `StArMap Client` is a client library to communicate with the _StArMap_ service, which is used to map a VM image build to its respective cloud marketplace(s) destination(s).

It's written to support applications running on `Python >= 3.8`.

This library has a minimum set of requirements (namely `attrs` and `requests`) and can be installed and used in any supported environment.

## Documentation

The documentation of `StArMap Client` is [available here](https://release-engineering.github.io/starmap-client/).

## Installation

To install this library go to the project's root directory and execute:

```{bash}
    pip install -r requirements.txt
    pip install .
```

## Usage

Initializing the client

```{python}
    # Import the library
    from starmap_client import StarmapClient

    # Instantiate the client
    client = StarmapClient(url="https://starmap.engineering.redhat.com/")
```

Querying the destinations of an image:

```{python}
    # Both statements will return a starmap_client.models.QueryResponse 
    object

    # Query by NVR
    query_response = client.query_image("sample-product-1.0.0-sp.vhd.xz")

    # Query by Name, Version
    query_response = client.query_image_by_name(name="sample-product", version="1.0.0")
```

## Development

### Prerequisites

The versions listed below are the one which were tested and work. Other versions can work as well.

- Install or create a `virtualenv` for `python` >= 3.8
- Install `tox` >= 3.25

### Dependency Management

To manage dependencies, this project uses [pip-tools](https://github.com/jazzband/pip-tools) so that
the dependencies are pinned and their hashes are verified during installation.

The unpinned dependencies are recorded in **setup.py** and the **requirements.txt** are regenerated
each time `tox` runs. Alternatively you can run `tox -e pip-compile` manually
to achieve the same result. To upgrade a package, use the `-P` argument of the `pip-compile` command.

When installing the dependencies use the command `pip install --no-deps --require-hashes -r requirements.txt`.

To ensure the pinned dependencies are not vulnerable, this project uses [safety](https://github.com/pyupio/safety),
which runs on every pull-request or can be run manually by `tox -e security`.

### Coding Standards

The codebase conforms to the style enforced by `flake8` with the following exceptions:

- The maximum line length allowed is 100 characters instead of 80 characters

In addition to `flake8`, docstrings are also enforced by the plugin `flake8-docstrings` with
the following exemptions:

- D100: Missing docstring in public module
- D104: Missing docstring in public package
- D105: Missing docstring in magic method

Additionally, `black` is used to enforce other coding standards.

To verify that your code meets these standards, you may run `tox -e lint`.

To automatically format your code you man run `tox -e autoformat`.

### Unit tests

To run unit tests use `tox -e py38,py39,py310,py311`.
