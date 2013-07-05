from bccvl_visualiser.models import TextWrapper

from bccvl_visualiser.models.api import (
    BaseAPI
    )

class RasterAPI(BaseAPI):

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
