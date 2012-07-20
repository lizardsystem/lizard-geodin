lizard-geodin
==========================================

`GeODin <http://www.geodin.com/>`_ (made by `Fugro <http://www.fugro.com/>`_)
is a modular data management solution. Lizard-geodin is a Lizard application
that couples Lizard and Geodin via Geodin's REST API.

The interaction with the REST API is on three separate levels:

- The API starting point (a model in our database) has a URL that returns a
  json with a list of projects (and the projects' URLs). They rarely
  change. This static data can basically be synced to the Lizard database.

  The API starting point admin page has a 'reload' action to re-import the
  projects.

- Every project also can be reloaded with an admin action. A project's json
  returns a hierarchy of location/investigation/datatype. A
  project/location/investigation/datatype combination (so: 4 foreign keys) has
  a list of points.

  This combination with 4 foreign keys and that list of points is represented
  in the database by a measurement object.

  The list of points also contains the latest value, which can be used for
  coloring icons on the map or so. So these measures could be renewed often or
  even on the fly: they contain the x/y location and the last value. OTOH, the
  hierarchy doesn't change and measures are only rarely added. But refreshing
  doesn't hurt too much.

- For every point, which also has a URL, Geodin returns the recent data values
  (3-7 days at the moment).
