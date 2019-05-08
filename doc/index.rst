.. fables documentation master file, created by
   sphinx-quickstart on Tue May  7 15:27:56 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to fables's documentation!
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules/api

Explore Features:
-----------------

* :ref:`genindex`


Installing Library
------------------

For General Use
~~~~~~~~~~~~~~~

If you use pip to manage your python packages and don't plan on making code changes \
you can run one of the following two commands to clone and install fables.

* If you use HTTPS protocol to connect to bitbucket run::


    pip install https://www.github.com/payscale/fables

If you don't use pip to manage your python packages it's as easy as cloning this repo \
and making sure you have the dependencies.

* Clone this repo with your favorite git tool.

* Dependencies can be found in the requirements.txt. To install dependencies::


    pip install -r /path/to/requirements.txt

For Development:
~~~~~~~~~~~~~~~~

If you plan to add features and/or bug-fix fables, you will need to clone this repo.

Once the repo has been cloned you can ``cd`` into the repo dir and run the following::

    pip install -e .

This installs fables in development mode, so as you make changes to the package you can test \
those changes without reinstalling the module.

Uninstalling
------------

If you only cloned the library via git, you can simply delete the repo from your system.

If you pip installed the library (either for general usage or development) run the following::

    pip uninstall fables

* NOTE: If you installed via ``pip install -e .`` you may need to manually delete the fables.egg-info file \
  that was created in your fables repo file to complete the uninstall.

Running Tests
-------------

Information on running tests here.

Adding Functionality
--------------------

Contributions are not only welcome, they are encouraged.

* Create a pull request and tag one or two people on the authoring team.

Updating Sphinx Documentation
-----------------------------

Our library is documented using Sphinx. One benefit of this approach is that it automatically pulls
docstrings from your added functionality to create new documentation. Check the text_cleaning.py file
to get an idea of the format your docstrings should follow. Once your pull request for new functionality
has been merged you can rebuild the documentation using the following steps:

* Make sure Sphinx is installed locally::


    pip install sphinx

* Also install the sphinxcontrib-napoleon extension::


    pip install sphinxcontrib-napoleon

* To re-build the documentation ``cd`` into the /doc subdirectory and run::


    make html

* The updated html files will be built into the _build/html and _buld/html/modules subdirectories

NOTE: If you add a new module, you will need to add it to the toctree within the index.rst and you will
also need to create an rst file for your module and place it under /docs/modules

Need More Help?
---------------

Just reach out to anyone on the DS team.


License
-------

The project is licensed under the Apache 2.0 license.
