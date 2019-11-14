Pata
====

Library in charge of loading, maintaining and refining data and databases related to Prismata (strategy game).

Install as library
--------------------

    **pip install pata**

Development environment
-----------------------

0. Virtual environment (look at virtualenvwrapper):

   Create:

    mkvirtualenv pata

   Activate:

    workon pata

1. Install dependencies:

    pip install -r requirements-dev.txt

2. Run tests:

    ./runtests.sh

3. Run linters:

    ./runlinters.sh

Databases configuration
-----------------------

- Read alembic/README.rst for more details (like using multiple engines) on migration configuration.

- To generate a new migration:

  alembic revision -m "message for migration" --autogenerate

- Apply everything until latest migration:

  alembic upgrade head

Command
-------

- Execute the following command to get help on how to use the units migration command:

  python pata/migrate_units.py -h
