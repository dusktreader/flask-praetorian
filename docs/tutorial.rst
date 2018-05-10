Tutorial
========

This tutorial will use the example code provided in the `example/`_ code
directory.,

Download the entire directory and save it on your machine where you will be
running through the tutorial.

Requirements
------------

This tutorial requires (outside of the normal python dependencies):

* sqlite
* a web-browser

About the api-tool
------------------

The custom api gui tool is itself a flask-app that uses html and javascript to
render the website. If you are curious about the code feel free to explore, but
don't let the implementation distract you: the author of flask-praetorian is
a back-end dev and javascript is not his strong-suit.

The main thing to focus on as you go through the tutorial is the structure of
the requests and responses. These will be shown by two text boxes at the bottom
of the gui tool.

If you do not wish to use the api tool for this tutorial, you could use a
tool designed for sending requests to an API such as Postman or curl. In either
case, the requests described in the 'request' box in the screenshots of the
api-tool can be used with the tool of your choice.

Starting up the servers
-----------------------

We will need to start up 4 different python/flask applications:

* `example/basic.py`_ is an api that shows basic jwt security concepts
* `example/refresh.py`_ is an api that shows jwt refreshing concepts
* `example/blacklist.py`_ is an api that shows jwt blacklisting concepts
* `example/api_tool.py`_ is the demonstration flask-app that accesses the apis

All four of these should be started. You may kick them off in separate
terminals, or as daemons. It's nice to watch the output from the apps in
terminals, but the api_tool should display all of the request/resonse info that
you need for this tutorial

The flask applications are started easily::

$ python example/basic.py

Each of the api applications runs on a different port to avoid collision. The
api-tool runs on port 5050, and that is where you will access the ui

Accessing the tool
------------------

Once you've started up all four flask apps, you can checkout the gui tool by
navigating to ``http://localhost:5050``

Tutorial Sections
-----------------

.. toctree::
   :glob:
   :maxdepth: 1

   Basic Tutorial <tutorial_basic>
   Refresh Tutorial <tutorial_refresh>
   Blacklist Tutorial <tutorial_blacklist>

.. _example/: https://github.com/dusktreader/flask-praetorian/tree/master/example
.. _example/basic.py: https://github.com/dusktreader/flask-praetorian/blob/master/example/basic.py
.. _example/refresh.py: https://github.com/dusktreader/flask-praetorian/blob/master/example/refresh.py
.. _example/blacklist.py: https://github.com/dusktreader/flask-praetorian/blob/master/example/blacklist.py
.. _example/api_tool.py: https://github.com/dusktreader/flask-praetorian/blob/master/example/api_tool.py
