.. StArMap Client documentation master file, created by
   sphinx-quickstart on Tue Jan  3 15:29:55 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

StArMap Client
==============

A client library to communicate with StArMap.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   client/client
   model/models
   session/session
   provider/provider

Quick Start
-----------

Install starmap_client:

::

    pip install starmap-client

In your python code, obtain a :class:`~starmap_client.StarmapClient` instance and
use it to communicate with ``StArMap``:

.. code-block:: python

    from starmap_client import StarmapClient
    import logging

    # Alternatively you can pass the api_version as well. Defaults to "v1".
    # client = StarmapClient(url="https://starmap.example.com", api_version="v1")
    client = StarmapClient(url="https://starmap.example.com")


Then it's possible to use the client object to call any API endpoint from ``StArMap``.

.. code-block:: python

    # Query image destinations by NVR
    query = client.query_image("sample-product-1.0.0-vhd.xz")

    # Query image destinations by name only
    query = client.query_image_by_name(name="sample-product")

    # Query image destinations by name and version
    query = client.query_image_by_name(name="sample-product", version="1.0.0")

    # Iterate over all policies from StArMap
    for policy in client.policies:
        # Do something
        ...

    # List all policies
    policies = client.list_policies()

    # Get a specific policy by its ID
    policy = client.get_policy(policy_id="426a3eac-8b9d-11ed-90ee-902e165594e8")

.. include:: client/usage.rst
