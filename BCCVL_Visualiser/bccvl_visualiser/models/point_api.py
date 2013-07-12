import mapscript
import os

from bccvl_visualiser.models import TextWrapper

from bccvl_visualiser.models.api import (
    BaseAPI
    )

class BasePointAPI(BaseAPI):

    @staticmethod
    def identifier():
        return "point"

    @staticmethod
    def description():
        desc = """\
The point API is responsible for visualising \
point data in CSV files.\
"""
        return desc

class PointAPIv1(BasePointAPI):
    """ v1 of the Point API"""

    DEFAULT_LAYER_NAME='DEFAULT'
    MAP_FILE_NAME = 'point_api_v1_map_file.map'

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
