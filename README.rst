lizard-geodin
==========================================

`GeODin <http://www.geodin.com/>`_ (made by `Fugro <http://www.fugro.com/>`_)
is a modular data management solution. Lizard-geodin is a Lizard application
that couples Lizard and Geodin via Geodin's REST API.

The interaction with the REST API is on three separate levels:

- Projects, location types etcetera rarely change. This static data can
  basically be synced to the Lizard database.

- The actual measures should be renewed often or even on the fly: they contain
  the x/y location and the last value.

- For every location, Geodin can give the recent historical data values.
