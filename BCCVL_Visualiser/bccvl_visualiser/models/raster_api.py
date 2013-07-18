import mapscript
import os

from bccvl_visualiser.models import TextWrapper
from bccvl_visualiser.models.mapscript_helper import MapScriptHelper

from bccvl_visualiser.models.api import (
    BaseAPI,
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
    """ v1 of the Raster API"""

    DEFAULT_LAYER_NAME='DEFAULT'
    MAP_FILE_NAME='raster_api_v1_map_file.map'
    TEST_250M_DATA_FILE_NAME='sample_250m_ascii_grid.tiff'
    TEST_1KM_DATA_FILE_NAME='sample_1km_ascii_grid.tiff'

    @staticmethod
    def version():
        return 1

    @staticmethod
    def get_map_and_ows_request_from_request(
        request,
        map_file_name=MAP_FILE_NAME
    ):
        """ Returns a mapscript.mapObj and a mapscript.OWSRequest

            Given a request object, and optionally a map_file path,
            generates a mapObj and a OWSRequest object.

            The OWSRequest object will be generated using
            the request's query_string.

            Additionally, default OWS params will be set if
            not already set.

        """

        map, ows_request = MapScriptHelper.get_map_and_ows_request_from_request(request, map_file_name)

        # Set the raster API v1's defaults on the OWS request.
        RasterAPIv1._set_ows_default_params_if_not_set(ows_request)

        return map, ows_request

    @staticmethod
    def set_data_for_map_layer_if_not_set(map, data_id, layer_name):
        """ Given a data_id, will set the LAYER's DATA value

            Will speak to the Data Manager and get a local copy of the
            data (represented by the data_id). Once this is done,
            it will move the data to the map's SHAPEPATH.

            Once the data is in the right directory (SHAPEPATH), the
            DATA value for the LAYER will be set accordingly.

        """

        if data_id != None:
            return MapScriptHelper.set_data_for_map_layer_if_not_set(map, data_id, layer_name)
        else:
            layer = map.getLayerByName(layer_name)

            if layer != None and layer.data == None:
                layer.data = RasterAPIv1.TEST_250M_DATA_FILE_NAME

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

    @staticmethod
    def _set_ows_default_params_if_not_set(ows_request):
        """ Set OWS Params to their default value (if not already set)"""
        layers = ows_request.getValueByName('LAYERS')
        if layers == None:
            ows_request.addParameter('LAYERS', RasterAPIv1.DEFAULT_LAYER_NAME)
