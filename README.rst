arundeckrun
===========

|codecov.io|

|wercker status|

A fork of the client library written in Python to interact with the
Rundeck API, the majority of which was created by Mark LaPerriere.

The fork exists mostly because the environment Antillion use it requires
it to be hosted on pypi, so updates must be pushed quickly. In addition,
the requirement to run tests against a live Rundeck is a no-no.

Rundeck (API) version compatibility:

Some calls are under active use/development, primarily:

-  Job imports: API v1+
-  Project archive imports: API v14+

All other calls *should* work correctly as long as they are not
deprecated or if Rundeck fail to correctly implement backwards
compatibility.

Target python version: 2.7 Should work (but not tested aagainst): 3

Installation
============

pip install arundeckrun

Use
---

::

    >>> from rundeck.client import Rundeck
    >>> rd = Rundeck('rundeck.server.com', api_token='SECRET_API_TOKEN')
    >>> rd.list_projects()
    [{
        'description': None,
        'name': 'TestProject',
        'resources': {'providerURL': 'http://localhost:8000/resources.xml'},
    }]
    >>> rd.list_jobs('TestProject')
    [{'description': 'Hello World!',
      'group': None,
      'id': 'a6e1e0f7-ad32-4b93-ba2c-9387be06a146',
      'name': 'HelloWorld',
      'project': 'TestProject'}]
    >>> rd.run_job('a6e1e0f7-ad32-4b93-ba2c-9387be06a146', argString={'from':'arundeckrun'})
    {'argstring': '-from arundeckrun',
     'date-started': datetime.datetime(2013, 7, 11, 18, 4, 24),
     'description': 'Plugin[localexec, nodeStep: true]',
     'href': 'http://rundeck.server.com/execution/follow/123',
     'id': '123',
     'job': None,
     'status': 'running',
     'user': 'arundeckrun'}

Tests
=====

Unit tests
----------

Unit tests are performed via tox.

To install tox and then run the tests:

::

    pip install tox
    tox

Integration tests
-----------------

*Note:* currently the integrations are not up-to-date and are not under
continous integration. Soon though…

Running the tests requires a running Rundeck server (the Rundeck
standalone jar works well) and an API token for said Rundeck server.

You’ll have to at least set the API token environment variable of
``RUNDECK_API_TOKEN`` but there are other environment variables to be
aware of. The list is below and can be found at the head of the
tests/\_\_init\_\_.py file. They should be fairly self-explanatory (OK,
RUNDECK\_PROTOCOL might not be self-explanatory… use either ‘http’ or
‘https’ there).

.. code-block:: bash

::

    RUNDECK_API_TOKEN
    RUNDECK_SERVER
    RUNDECK_PORT
    RUNDECK_PROTOCOL

Next clone the repo.

.. code-block:: bash

::

    git clone https://github.com/marklap/arundeckrun

.. note:: act

.. |codecov.io| image:: https://codecov.io/github/Antillion/rundeckrun/coverage.svg?branch=master
   :target: https://codecov.io/github/Antillion/rundeckrun?branch=master
.. |wercker status| image:: https://app.wercker.com/status/57e663b27aba00b9b7aabe4ea7b8208a/m/master
   :target: https://app.wercker.com/project/bykey/57e663b27aba00b9b7aabe4ea7b8208a