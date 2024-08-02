Session
=======

Define a session to communicate with StArMap over HTTPS.


Interface
---------
.. autoclass:: starmap_client.session.StarmapBaseSession
   :members:
   :special-members: __init__

Implementations
---------------

Network based (Online)
^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: starmap_client.session.StarmapSession
   :members:
   :special-members: __init__

Mock based (Offline)
^^^^^^^^^^^^^^^^^^^^
.. autoclass:: starmap_client.session.StarmapMockSession
   :members:
   :special-members: __init__
