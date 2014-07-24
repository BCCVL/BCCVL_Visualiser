import mapscript
import os

from bccvl_visualiser.models.bccvl_map import GeoTiffBCCVLMap
from bccvl_visualiser.models.api import BaseAPI

class BaseRasterAPI(BaseAPI):

    @staticmethod
    def identifier():
        return "raster"

    @staticmethod
    def description():
        desc = """\
The raster API is responsible for processing \
raster image files.\
"""
        return desc

class RasterAPIv1(BaseRasterAPI, GeoTiffBCCVLMap):
    """ v1 of the Raster API"""

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
            'version': _class.version()
        }

        return return_dict

    def __init__(self, **kwargs):
        """ init the instance """
        super(RasterAPIv1, self).__init__(**kwargs)
