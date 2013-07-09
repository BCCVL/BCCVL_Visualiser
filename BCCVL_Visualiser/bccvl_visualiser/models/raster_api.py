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
    def map_object_from_wms_request(
        request,
        map_file=MAP_FILE_PATH
    ):
        wms_request = mapscript.OWSRequest()
        wms_request.loadParams()

        map = mapscript.mapObj(RasterAPIv1.MAP_FILE_PATH)
        map.OWSRequest(wms_request)
        return map

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
