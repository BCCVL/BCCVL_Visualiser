from sqlalchemy import (
    Column,
    Integer,
    Text,
    Unicode,
    ForeignKey,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from geoalchemy import *

from zope.sqlalchemy import ZopeTransactionExtension

import requests

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

DEFAULT_PROJECTION = 4326

class Species(Base):
    __tablename__ = 'species'
    id = Column(Integer, primary_key=True)
    name = Column(Text)

    ALA_SPECIES_SERVICE_URL = "http://biocache.ala.org.au/ws/webportal/species"

    def __init__(self, name):
        """ Species constructor

            Takes the following params:
                * name         : The species' name
        """
        self.name = name

    def by_name(class_):
        """ Sort the Species by name
        """
        Species = class_
        q = Session.query(Species)
        q = q.order_by(Species.name)
        return q

    @staticmethod
    def ala_search_for_species(species_name):
        """ Searches ALA for the given species
        """
        query_params = { 'q': species_name }
        r = requests.get(Species.ALA_SPECIES_SERVICE_URL, params=query_params)
        json_data = r.json()
        return json_data

class Occurrence(Base):
    __tablename__ = 'occurrences'
    id = Column(Integer, primary_key=True)
    # The occurrence MUST be associated with a species
    species_id = Column(Integer, ForeignKey("species.id"), nullable=False)
    location = GeometryColumn(Point(2))

    def __init__(self, species, location_wkt, projection=DEFAULT_PROJECTION):
        """ Occurrence constructor

            Takes the following params:
                * species      : The species the occurrence will be associated with
                * location_wkt : A WKT description of the occurrence Point
                * projection   : The projection as an integer
        """
        self.species_id = species.id
        self.location = WKTSpatialElement(location_wkt, projection)
