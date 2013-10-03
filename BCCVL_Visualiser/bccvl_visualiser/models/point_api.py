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

import requests
import hashlib

class BasePointAPI(BaseAPI):

    @staticmethod
    def identifier():
        return "point"

    @staticmethod
    def description():
        desc = """\
The point API is responsible for visualising \
point data in CSV files. The point data is expected to be in the 4326 \
projection, i.e. decimal degrees latitude/longitude\
"""
        return desc

class PointAPIv1(BasePointAPI):
    """ v1 of the Point API"""

    DEFAULT_LAYER_NAME='DEFAULT'
    MAP_FILE_NAME = 'point_api_v1_map_file.map'
    TEST_RED_KANGAROO_DATA_FILE_NAME = 'test_red_kangaroo_data.csv'
    TEST_MAGPIE_DATA_FILE_NAME = 'test_magpie_data.csv'

    class OccurrencesDialect(csv.Dialect):
        strict = True
        skipinitialspace = True
        quoting = csv.QUOTE_MINIMAL
        delimiter = ','
        quotechar = '"'
        lineterminator = '\n'


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

        # Set the point API v1's defaults on the OWS request.
        PointAPIv1._set_ows_default_params_if_not_set(ows_request)

        return map, ows_request

    @staticmethod
    def set_connection_for_map_connection_if_not_set(request, map, data_id, layer_name):
        """ Given a data_id, will lookup the data item via the Data Manager

            Will speak directly to the Data Mover, and download the file.
            Once this is done, it will move the data to the map's SHAPEPATH.

            Once the data is in the right directory (SHAPEPATH), the
            DATA value for the LAYER will be set accordingly.

        """
        log = logging.getLogger(__name__)

        layer = map.getLayerByName(layer_name)

        if layer != None and layer.connection == None:
            if data_id == None:
                connection = PointAPIv1._get_connection(request, PointAPIv1.TEST_MAGPIE_DATA_FILE_NAME)
                log.debug("Setting map layer connection to: %s", connection)
                layer.connection = connection
            else:
                # TODO -> This is where we should talk to the data manager and
                # get access to the data file.
                #
                # For now, just set the map layer's data to our test data
                raise NotImplementedError("TODO - This method needs to handle a data_id")

    @staticmethod
    def set_connection_for_map_connection_if_not_set_url(request, map, data_url, layer_name):
        """ Given a data_url, will set the LAYER's DATA value

            Will speak directly to the web server, and download the file.
            Once this is done, it will move the data to the map's SHAPEPATH.

            Once the data is in the right directory (SHAPEPATH), the
            DATA value for the LAYER will be set accordingly.

        """
        log = logging.getLogger(__name__)

        # generate a hash of the url
        hash_string = hashlib.sha224(data_url).hexdigest()
        file_name = hash_string + '.csv'
        # work out the map file path
        map_file_path = MapScriptHelper.get_path_to_map_data_file(request, file_name)

        # get the data from the url, only if we don't already have it
        if not os.path.isfile(map_file_path):
            r = requests.get(data_url, verify=False)
            r.raise_for_status()

            dirname, filename = os.path.split(os.path.abspath(map_file_path))

            if not os.path.isdir(dirname):
                os.makedirs(dirname)

            # write the data from the url to the map file path
            output = open(map_file_path,'wb')
            output.write(r.content)
            output.close()

        lng_column = None
        lat_column = None

        if PointAPIv1._check_if_occurrences_csv_valid(('SPPCODE', 'LNGDEC', 'LATDEC'), map_file_path, lat='LATDEC', lng='LNGDEC'):
            lng_column = 'LNGDEC'
            lat_column = 'LATDEC'
        elif PointAPIv1._check_if_occurrences_csv_valid(('lon', 'lat'), map_file_path, lat='lat', lng='lon'):
            lng_column = 'lon'
            lat_column = 'lat'
        else:
            os.remove(map_file_path)
            raise Exception("Problem parsing Occurrence CSV file")

        layer = map.getLayerByName(layer_name)

        if layer != None and layer.connection == None:
            connection = PointAPIv1._get_connection(request, file_name, lng_column, lat_column)
            log.debug("Setting map layer connection to: %s", connection)
            layer.connection = connection


    @staticmethod
    def _check_if_occurrences_csv_valid(field_names, file_path, lng=None, lat=None):
            validator = CSVValidator(field_names)

            # basic header and record length checks
            validator.add_header_check('EX1', 'bad header')
            validator.add_record_length_check('EX2', 'unexpected record length')

            if lng:
                # some simple value checks
                validator.add_value_check(lng, float,
                              'EX3', "%s must be a float" % lng)

            if lat:
                validator.add_value_check(lat, float,
                              'EX4', "%s must be a float" % lat)

            with open(file_path, 'rb') as csvfile:
                reader = csv.reader(csvfile, PointAPIv1.OccurrencesDialect)
                problems = validator.validate(reader, limit=20)

                if len(problems) > 0:
                    return False
                else:
                    return True

    @staticmethod
    def _set_ows_default_params_if_not_set(ows_request):
        """ Set OWS Params to their default value (if not already set)"""

        # Used by wfs requests
        layer = ows_request.getValueByName('LAYER')
        if layer == None:
            ows_request.addParameter('LAYER', PointAPIv1.DEFAULT_LAYER_NAME)

        # Used by wms requests
        layers = ows_request.getValueByName('LAYERS')
        if layers == None:
            ows_request.addParameter('LAYERS', PointAPIv1.DEFAULT_LAYER_NAME)


    @staticmethod
    def _get_connection(request, file_name, x_column_name='lon', y_column_name='lat'):
        file_path = MapScriptHelper.get_path_to_map_data_file(request, file_name)
        connection = """"\
<OGRVRTDataSource>
    <OGRVRTLayer name='{0}'>
        <SrcDataSource>{1}</SrcDataSource>
        <LayerSRS>WGS84</LayerSRS>
        <GeometryField encoding='PointFromColumns' x='{2}' y='{3}'/>
        <GeometryType>wkbPoint</GeometryType>
    </OGRVRTLayer>
</OGRVRTDataSource>""".format(os.path.splitext(file_name)[0], file_path, x_column_name, y_column_name)

        return connection

