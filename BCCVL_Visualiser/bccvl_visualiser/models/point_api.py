import mapscript
import os
import logging
import csv

from bccvl_visualiser.models.bccvl_map import OccurrencesBCCVLMap
from bccvl_visualiser.models.api import BaseAPI

class BasePointAPI(BaseAPI):

    @staticmethod
    def identifier():
        return "point"

    @staticmethod
    def description():
        desc = """\
The point API is responsible for visualising \
point data in CSV files. The point data is expected to be in the 4326 \
projection, i.e. decimal degrees latitude/longitude.\
"""
        return desc

class PointAPIv1(BasePointAPI, OccurrencesBCCVLMap):
    """ v1 of the Point API"""

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
        super(PointAPIv1, self).__init__(**kwargs)


