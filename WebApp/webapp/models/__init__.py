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

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


#class MyModel(Base):
#    __tablename__ = 'models'
#    id = Column(Integer, primary_key=True)
#    name = Column(Text, unique=True)
#    value = Column(Integer)
#
#    def __init__(self, name, value):
#        self.name = name
#        self.value = value

class Species(Base):
    __tablename__ = 'species'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    description = Column(Text)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def by_name(class_):
        Species = class_
        q = Session.query(Species)
        q = q.order_by(Species.name)
        return q

class Occurrence(Base):
    __tablename__ = 'occurrences'
    id = Column(Integer, primary_key=True)

    # The occurrence MUST be associated with a species
    species_id = Column(Integer, ForeignKey("species.id"), nullable=False)
    location = GeometryColumn(Point(2))

    # Takes
    # location as wkt
    # 
    def __init__(self, species, location_wkt, projection):
        self.species_id = species.id
        self.location = WKTSpatialElement(location_wkt, projection)
