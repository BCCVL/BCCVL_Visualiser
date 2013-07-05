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

class Occurrence(Base):
    __tablename__ = 'occurrences'
    id = Column(Integer, primary_key=True)
    # The occurrence MUST be associated with a species
    species_id = Column(Integer, ForeignKey("species.id"), nullable=False)
    species = relationship("Species", backref=backref('occurrences', order_by=id))
    location = Column(Geometry(geometry_type='POINT', srid=DEFAULT_PROJECTION))

    def __init__(self, location_wkt, projection=DEFAULT_PROJECTION):
        """ Occurrence constructor

            Takes the following params:
                * location_wkt : A WKT description of the occurrence Point
                * projection   : The projection as an integer
        """
        self.location = WKTElement(location_wkt, srid=projection)
