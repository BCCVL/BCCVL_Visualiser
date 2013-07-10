import mapscript
import os

from bccvl_visualiser.models import TextWrapper

from bccvl_visualiser.models.api import (
    BaseAPI
    )


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

class RasterAPIv1(BaseRasterAPI):
    """v1 of the version of the Raster API"""


    MAP_FILE_PATH = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..",
        "map_files",
        "raster_api_v1_map_file.map"
    )


    @staticmethod
    def version():
        return 1

    @staticmethod
    def get_map_and_ows_request_from_from_request(
        request,
        map_file=MAP_FILE_PATH
    ):
        """ Returns a mapscript.mapObj and a mapscript.OWSRequest

            Given a request object, and optionally a map_file path,
            generates a mapObj and a OWSRequest object.

            The OWSRequest object will be generated using
            the request's query_string.

        """

        map = mapscript.mapObj(RasterAPIv1.MAP_FILE_PATH)

        ows_request = mapscript.OWSRequest()
        ows_request.loadParamsFromURL(request.query_string)

        return map, ows_request

    @classmethod
    def to_dict(_class):
        """Returns a dict representation of the API

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
