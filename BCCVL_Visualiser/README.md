BCCVL_Visualiser README
========================

Getting Started
---------------

- cd <directory containing this file>

- $venv/bin/python bootstrap.py

- ./bin/buildout

- ./bin/pserve development.ini

Folder Structure
----------------

    - map_files /
      Where our map files are stored. The contents of this directory are specific
      to map script (or map server). These files are used by the Map classes defined
      in this file: bccvl_visualiser/models/bccvl_map.py

        - default.map
            This is just a general mapfile. This is the default map file used by the
            BCCVLMap base class. In production, it is unlikely that you will use
            this general map file.
        - default_occurrences.map
            This is the default map file used to render occurrence/absence files.
        - default_raster.map
            This is the default map file used to render raster files.
        - symbols.map
            This file defines the 'symbol set' for the other map files.
        - point_api_v1_csv_to_geo_json_transform.tmpl
            This file defines the transform to convert a csv occurrence file into GeoJSON.



    - bccvl_visualiser /
      Top level pyramid source code directory

        - __init__.py
        Where our view routes are defined. The config is read in at this point 
        and can be passed out as static config to other classes.
        Responsible for configuring our cache, map classes, data manager and data mover.

        - exceptions /
        Where our custom exceptions are defined.

        - invariants /
        Where our custom invariants are defined. Invariants are
        attached to interfaces, and define expected values or states.
        If an invariant fails, it should likely throw an exception.
        Consider invariants just like pre-conditions or assertions.
        See here for more information:
        http://docs.zope.org/zope.interface/README.html#invariants

        - scripts /
        Where we store our helper scripts.

        - static /
        Where we store static assets that pyramid will serve at /static. Static
        assets are cached for 3600 seconds (this can be changed). See bccvl_visualiser/__init__.py

        - models /
        Where the class files are for non view/template code. Note: This directory
        doesn't just contain models, it also contains helper classes.

            - __init__.py
            Imports all the other models. A convenience file.

            - ala_helper.py
            Not used. Provides some basic support for searching ALA.

            - api.py
            Provides the Base class (BaseAPI) for all APIs. All APIs are expected
            to conform to this 'abstract class'.

            - api_collection.py
            Provides an interface to gain access to the APIs via their identifiers.

            - auto_detect_api.py
            The most useful API. This API is responsible for detecting what 'type'
            of file the user is wanting to visualsie, and redirects them to the
            appropriate API. This should ideally be the only API that is aware of the
            others.

            - bccvl_map.py
            This is a useful helper class. This class extends the MapScript Map object.
            This class will probably be the most 'foreign' to non-GIS programmers.
            The BCCVLMap extends mapObj. MapScript provides a Python SWIG interface.
            The mapObj class is defined here: http://mapserver.org/mapscript/mapscript.html#mapobj
            The general MapScript SWIG documentation is available here:
            http://mapserver.org/mapscript/mapscript.html

            BCCVLMap is extended by two classes: OccurrencesBCCVLMap and GeoTiffBCCVLMap.
            The OccurrencesBCCVLMap is also currently responsible for rendering absences.
            This is because both files conform to the same latitude/longitude column conventions.

            To understand the BCCVLMap class, you'll likely need to learn some mapscript.

            - csv_api.py
            This API is responsible for rendering general CSV files. It just
            puts them in a nice html table.

            - html_api.py
            This API is responsible for rendering general html files.
            Currently, due to a lack of available metadata, the html api needs
            to apply secret plone knowledge, and rewrite relative URLs inside
            general html files. I very much hope this HACK can be removed
            at some point in the future, but until this kind of metadata is
            made available, the HACK will suffice.

            Look for this function: replace_urls(_class, in_str, data_url)

            - png_api.py
            This API is responsible for rendering png files.

            - point_api.py
            This API is responsible for rendering occurrence and absence files.
            Any CSV file with a lat/lon column can be rendered via this api.

            - r_api.py
            This API is responsible for rendering R text files. I use a javascript
            library called rainbow to syntax highlight the R file.

            The is the default (fallback) api for auto_detect. This is just because the R
            API can render general text with some basic level of syntax highlighting.

            - raster_api.py
            This API is responsible for rendering .tif files (GeoTiff).

            - external_api /
            Where the class files are that are responsible for handling interaction
            with external apis. Specifically, this is where the data_mover and
            data_manager support code should live.

                - data_mover.py
                This file contains the: IDataMover, FDataMover, LocalDataMover, and DataMover classes.

                IDataMover: the interface that a data mover implementation is expected to conform to.

                FDataMover: the factory that switches between LocalDataMover and DataMover based
                on the current FDataMover config variable `local` (boolean).
                FDataMover was added to allow the visualiser to be tested in isolation
                of the real data mover.

                DataMover: Is the "real" implementation of the data mover. This implementation
                uses the xmlrpc interface provided by the BCCVL Data Mover.

                LocalDataMover: Is our own implementation of the data mover interface. It conforms
                to the interface, using the requests library. This implementation is used when
                testing. It is worth noting that the LocalDataMover class extends the DataMover
                class, and simply overrides some of the DataMover functions.

                Note regarding testing:
                When writing test cases, you should set the FDataMover local variable
                to True when setting up the test, and to False when tearing down the test.
                This will ensure that the LocalDataMover is used during your tests.

                    class TestClass(unittest.TestCase):

                        def setUp(self):
                            FDataMover.local = True
                            ...

                            def tearDown(self):
                            FDataMover.local = False
                            ...


Common Requirements
=====================

The following is a list of common requirements, and how they can be used:

    img manip -> Pillow (python img lib)
    pyramid_tm (transaction management)
    pyramid_beaker -> session management
    pyramid_deform -> form generation schema (default -> colander)
    colander_alchemy -> takes sql alchemy models into colander for use in forms
    pyramid_debugtoolbar -> AWESOME (installed by default) -> performance of views/functions
    pyramid_fanstatic -> static resource sharing (where dependency management is important)
    pyramid_mailer -> sending emails
    sunburnt       -> talks to apache solar (enterprise search engine)
    natural        -> (might be useful) data conversion, making it human readable
    feedparser     -> pasrses ATOM and RSS
    geojson        -> producing GeoJSON from a geometry
    shapely        -> geom stuff, centroid, area
    bleach         -> html filtering (whitelisting)
    docutils       -> converting reST
    dogpile.cache  -> cache regions, lets you cache the result of queries


ALA Web Services API
===========================

http://biocache.ala.org.au/ws

Get all the occurrences zipped for EMU, using the LSID as the search keyword. Only give me the longitude, latitude and raw_taxon_name

http://biocache.ala.org.au/ws/webportal/occurrences.gz?q=lsid:urn%3Alsid%3Abiodiversity.org.au%3Aafd.taxon%3Af5b22be3-b523-488a-89fc-39bd21aefb6d&fl=raw_taxon_name,longitude,latitude&pageSize=10000
