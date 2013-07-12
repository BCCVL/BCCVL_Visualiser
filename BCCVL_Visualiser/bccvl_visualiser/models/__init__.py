from textwrap import TextWrapper

from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    )

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
TextWrapper = TextWrapper()

DEFAULT_PROJECTION = 4326

from bccvl_visualiser.models.mapscript_helper import *
from bccvl_visualiser.models.species import *
from bccvl_visualiser.models.occurrence import *
from bccvl_visualiser.models.raster_api import *
from bccvl_visualiser.models.point_api import *
from bccvl_visualiser.models.api_collection import *
