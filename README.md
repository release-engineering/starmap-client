# StArMap Client

The client implementation for [StArMap](https://gitlab.cee.redhat.com/stratosphere/starmap).

[![pipeline](https://gitlab.cee.redhat.com/stratosphere/starmap-client/badges/main/pipeline.svg)](https://gitlab.cee.redhat.com/stratosphere/starmap-client/-/pipelines)
[![Quality Gate Status](https://sonarqube.corp.redhat.com/api/project_badges/measure?project=stratosphere_starmap-client&metric=alert_status&token=cc200ebb1eb3be0a1ce831185a3bbc1adfafd47e)](https://sonarqube.corp.redhat.com/dashboard?id=stratosphere_starmap-client)
[![coverage](https://gitlab.cee.redhat.com/stratosphere/starmap-client/badges/main/coverage.svg)](https://gitlab.cee.redhat.com/stratosphere/starmap-client/-/jobs)
[![releases](https://gitlab.cee.redhat.com/stratosphere/starmap-client/-/badges/release.svg)](https://gitlab.cee.redhat.com/stratosphere/starmap-client/-/releases/)

## Overview

The `StArMap Client` is a client library to communicate with [StArMap](https://gitlab.cee.redhat.com/stratosphere/starmap).

It's written to support applications running on `Python >= 3.8`.

This library has a minimum set of requirements (namely `attrs` and `requests`) and can be installed and used in any supported environment.

## Documentation

The documentation of `StArMap Client` is [available here](https://stratosphere.pages.redhat.com/starmap-client/).

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
