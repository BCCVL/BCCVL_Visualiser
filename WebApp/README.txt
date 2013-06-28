WebApp README
==================

Getting Started
---------------

- cd <directory containing this file>

- $venv/bin/python setup.py develop

- $venv/bin/initialize_WebApp_db development.ini

- $venv/bin/pserve development.ini

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


How To Doc
=======================

def self.Cat(a)
    """ My Cat class

    These be me params
        *a* is a A
    """

    hello = 's
    .
