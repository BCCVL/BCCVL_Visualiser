import mapscript
import os
import logging
import csv
from csvvalidator import *


from bccvl_visualiser.models import TextWrapper
from bccvl_visualiser.models.bccvl_map import *

from bccvl_visualiser.models.api import (
    BaseAPI
    )

class BaseCSVAPI(BaseAPI):

    @staticmethod
    def identifier():
        return "csv"

    @staticmethod
    def description():
        desc = """\
The CSV API is responsible for visualising \
general CSV files.\
"""
        return desc

class CSVAPIv1(BaseCSVAPI):
    """ v1 of the CSV API"""

    @staticmethod
    def version():
        return 1

    @classmethod
    def to_dict(_class):
        """ Returns a dict representation of the API

            This dict identifies the API, and its
            general purpose. More specific information about the
            API is defined at the specific version level of the API.
        """
        return_dict = {
            'name':         _class.identifier(),
            'description':  _class.description(),
            'version':      _class.version()
        }

        return return_dict

    def __init__(self, **kwargs):
        """ init the instance """
        super(CSVAPIv1, self).__init__(**kwargs)


