Usage
-----

The :class:`~starmap_client.StarmapClient` can be used to query the StArMap service over network and/or
locally.

In the subsections below you can find how to properly use the client for different
query use-cases.

Online Usage
^^^^^^^^^^^^

In this mode the :class:`~starmap_client.StarmapClient` will always request data from the server over the network.

.. code-block:: python

   from starmap_client import StarmapClient

   # Initialize the online client with the URL only
   client = StarmapClient(url="https://starmap.example.com", api_version="v1")

   # Alternatively you can create the session and inject it
   from starmap_client.session import StarmapSession
   session = StarmapSession("https://starmap.example.com", api_version="v1", retries=5, backoff_factor=5.0)
   client = StarmapClient(session=session)
   ...
   # Query
   client.query_image("sample-product-1.0.0-vhd.xz")
   client.query_image_by_name(name="sample-product", version="1.0.0")

Note that either ``url`` or ``session`` must be passed to the client to instantiate the object.


Offline Usage
^^^^^^^^^^^^^

In this mode the :class:`~starmap_client.StarmapClient` will always request data from a local `provider`_ instead of using the network.

.. code-block:: python

   import json
   from starmap_client import StarmapClient
   from starmap_client.session import StarmapMockSession
   from starmap_client.models import QueryResponse
   from starmap_client.providers import InMemoryMapProvider

   # Load the QueryResponse models from somewhere
   with open("path_to_your_data.json", 'r') as f:
      qr_data = json.load(f)

   # Create the offline client
   qr = QueryResponse.from_json(qr_data)
   responses = [qr]  # in this case it only contains 1 object, but it supports more
   provider = InMemoryMapProvider(responses)
   session = StarmapMockSession("fake.starmap.com", "v1")
   client = StarmapClient(session=session, provider=provider)

   # Query
   client.query_image("sample-product-1.0.0-vhd.xz")
   client.query_image_by_name(name="sample-product", version="1.0.0")

Hybrid Usage:
^^^^^^^^^^^^^

In this mode the :class:`~starmap_client.StarmapClient` will first request data from a local `provider`_ and 
only proceed to query over network if the local provider doesn't have the requested mapping.

.. code-block:: python

   import json
   from starmap_client import StarmapClient
   from starmap_client.models import QueryResponse
   from starmap_client.providers import InMemoryMapProvider

   # Load the QueryResponse models from somewhere
   with open("path_to_your_data.json", 'r') as f:
      qr_data = json.load(f)

   # Create the offline client
   qr = QueryResponse.from_json(qr_data)
   responses = [qr]  # in this case it only contains 1 object, but it supports more
   provider = InMemoryMapProvider(responses)
   client = StarmapClient(url="https://starmap.example.com", provider=provider)

   # Query
   client.query_image("sample-product-1.0.0-vhd.xz")
   client.query_image_by_name(name="sample-product", version="1.0.0")

.. _session: ../session/session.html
.. _provider: ../provider/provider.html
