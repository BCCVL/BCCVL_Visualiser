import requests

from bccvl_visualiser.models import DBSession, Base, DEFAULT_PROJECTION

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
    relationship,
    backref,
    )

from geoalchemy2 import *

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

