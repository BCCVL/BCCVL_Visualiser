import mapscript
import csv
from mapscript import mapObj, OWSRequest
import logging
import os
import threading

import requests
import hashlib

from csvvalidator import *

class BCCVLMap(mapObj):
    """ Our custom BCCVL mapObj.

        Provides additional utitlity functions on top of
        mapscript's mapObj class
    """

    MAPSCRIPT_RLOCK = threading.RLock()
    MAP_FILES_ROOT_PATH      = None
    MAP_DATA_FILES_ROOT_PATH = None

    DEFAULT_LAYER_NAME = 'DEFAULT'

    EXTENSION = ''
    DEAFULT_MAP_FILE_NAME = 'default.map'

    @classmethod
    def configure_from_config(class_, settings):
        class_.MAP_FILES_ROOT_PATH      = settings['bccvl.mapscript.map_files_root_path']
        class_.MAP_DATA_FILES_ROOT_PATH = settings['bccvl.mapscript.map_data_files_root_path']

    def __init__(self, map_file_name=None, data_id=None, data_url=None, layer_name=None, query_string=None, **kwargs):
        """ initialise the map instance from a data_url """
        if data_id and data_url:
            raise ValueError("A BCCVLMap can't have both a data_id and a data_url")
        elif data_id:
            self._init_from_data_id(data_id)
        elif data_url:
            self._init_from_data_url(data_url)
        else:
            raise ValueError("A BCCVLMap must have a data_id or a data_url")

        # If the user didn't override the map file name,
        # then use this class's default map file name
        if map_file_name is None:
            map_file_name = self.__class__.DEFAULT_MAP_FILE_NAME
        self.map_file_name = map_file_name

        # If the user didn't override the layer name,
        # then use this class's default layer name
        if layer_name is None:
            layer_name = self.__class__.DEFAULT_LAYER_NAME
        self.layer_name = layer_name

        self.map_file_path = self.__class__.get_map_file_path(map_file_name)

        super(BCCVLMap, self).__init__(self.map_file_path, **kwargs)

        self._set_map_defaults_if_not_set()
        self.set_ows_request_from_query_string(query_string)

    def _init_from_data_id(self, data_id):
        self.data_id = data_id
        raise NotImplementedError("data_id is not yet supported")

    def _init_from_data_url(self, data_url):
        """ initialise the map instance from a data_url """
        self.data_url = data_url

        # generate a hash of the url
        hash_string = hashlib.sha224(self.data_url).hexdigest()

        self.file_name = hash_string + self.__class__.EXTENSION
        self.data_file_path = self.__class__.get_path_to_map_data_file(self.file_name)

        with self.__class__.MAPSCRIPT_RLOCK:
            if not os.path.isfile(self.data_file_path):
                self._download_data_to_file()

    def set_ows_request_from_query_string(self, query_string):
        log = logging.getLogger(__name__)
        ows_request = OWSRequest()

        # loadParamsFromURL causes a seg fault if passed an empty string.
        # Don't pass it an empty string...
        if ( ( type(query_string) == str ) and ( query_string.strip() != '' ) ):
            ows_request.loadParamsFromURL(query_string)

        if (ows_request.getValueByName('LAYER') is None):
            ows_request.addParameter('LAYER', self.layer_name)

        if (ows_request.getValueByName('LAYERS') is None):
            ows_request.addParameter('LAYERS', self.layer_name)

        self.ows_request = ows_request

    def _download_data_to_file(self):
        r = requests.get(self.data_url, verify=False)
        r.raise_for_status()

        # Make sure only one thread is trying to check for
        # the existance of, or trying to write the file
        # at any time.
        with self.__class__.MAPSCRIPT_RLOCK:
            dirname, filename = os.path.split(os.path.abspath(self.data_file_path))

            if not os.path.isdir(dirname):
                os.makedirs(dirname)

            # write the data from the url to the map file path
            output = open(self.data_file_path,'wb')
            output.write(r.content)
            output.close()

    @classmethod
    def get_path_to_map_data_file(class_, data_file_name):
        log = logging.getLogger(__name__)

        map_data_files_root_path = class_.MAP_DATA_FILES_ROOT_PATH

        return_value = os.path.join(map_data_files_root_path, data_file_name)

        log.debug('Map data files root path: %s', map_data_files_root_path)
        log.debug('Map data file path: %s', return_value)

        return return_value

    @classmethod
    def get_map_file_path(class_, map_file_name):
        """ Returns the full os system path to the mapfile

            Uses the application config
            to look up the root map files path (where the map files are stored),
            and then joins this with the provided map_file_name argument.

        """

        log = logging.getLogger(__name__)

        map_files_root_path = class_.MAP_FILES_ROOT_PATH

        return_value = os.path.join(map_files_root_path, map_file_name)

        log.debug('Map files root path: %s', map_files_root_path)
        log.debug('Map file path: %s', return_value)

        return return_value

    def _set_map_defaults_if_not_set(self):
        """ Default the map's attributes """
        log = logging.getLogger(__name__)

        # Default the map attributes:
        #   * shapepath: the path to data files
        if self.shapepath == None:
            map_data_files_root_path = self.__class__.MAP_DATA_FILES_ROOT_PATH
            log.debug("Setting mapObj.shapepath as not already set. Set to: %s", map_data_files_root_path)
            self.shapepath = map_data_files_root_path


    def render(self):
        """ Render the map """
        map_image = None
        map_image_content_type = None
        retval = None

        with self.__class__.MAPSCRIPT_RLOCK:
            mapscript.msIO_installStdoutToBuffer()
            retval = self.OWSDispatch(self.ows_request)
            map_image_content_type = mapscript.msIO_stripStdoutBufferContentType()
            map_image = mapscript.msIO_getStdoutBufferBytes()
            mapscript.msIO_resetHandlers()

        return map_image, map_image_content_type, retval

class GeoTiffBCCVLMap(BCCVLMap):
    EXTENSION = ".tif"
    DEFAULT_MAP_FILE_NAME = "default_geo_tiff.map"

    def _set_map_defaults_if_not_set(self):
        """ Default the map's attributes """
        super(GeoTiffBCCVLMap, self).__init__(**kwargs)

        log = logging.getLogger(__name__)

        # Default the layer attributes:
        #   * data: the file path relative to shape path
        layer = self.getLayerByName(self.layer_name)
        if layer != None and layer.data == None:
            log.debug("Setting mapObj.layer.data as not already set. Set to: %s", self.file_name)
            layer.data = self.file_name

class OccurrencesBCCVLMap(BCCVLMap):
    EXTENSION = ".csv"
    DEFAULT_MAP_FILE_NAME = "default_occurrences.map"

    class OccurrencesDialect(csv.Dialect):
        strict = True
        skipinitialspace = True
        quoting = csv.QUOTE_MINIMAL
        delimiter = ','
        quotechar = '"'
        lineterminator = '\n'


    def __init__(self, **kwargs):
        super(OccurrencesBCCVLMap, self).__init__(**kwargs)
        self.set_connection_for_map_connection_if_not_set()

    def set_connection_for_map_connection_if_not_set(self):
        log = logging.getLogger(__name__)
        layer = self.getLayerByName(self.layer_name)

        if self.__class__._check_if_occurrences_csv_valid(('SPPCODE', 'LNGDEC', 'LATDEC'), self.data_file_path, lat='LATDEC', lng='LNGDEC'):
            lng_column = 'LNGDEC'
            lat_column = 'LATDEC'
        elif self.__class__._check_if_occurrences_csv_valid(('lon', 'lat'), self.data_file_path, lat='lat', lng='lon'):
            lng_column = 'lon'
            lat_column = 'lat'
        else:
            os.remove(self.data_file_path)
            raise ValueError("Problem parsing Occurrence CSV file")

        if layer != None and layer.connection == None:
            connection = self._get_connection(lng_column, lat_column)
            log.debug("Setting map layer connection to: %s", connection)
            layer.connection = connection

    def _get_connection(self, x_column_name='lon', y_column_name='lat'):
        connection = """"\
<OGRVRTDataSource>
    <OGRVRTLayer name='{0}'>
        <SrcDataSource>{1}</SrcDataSource>
        <LayerSRS>WGS84</LayerSRS>
        <GeometryField encoding='PointFromColumns' x='{2}' y='{3}'/>
        <GeometryType>wkbPoint</GeometryType>
    </OGRVRTLayer>
</OGRVRTDataSource>""".format(os.path.splitext(self.file_name)[0], self.data_file_path, x_column_name, y_column_name)

        return connection

    @classmethod
    def _check_if_occurrences_csv_valid(class_, field_names, file_path, lng=None, lat=None):
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

            with class_.MAPSCRIPT_RLOCK:
                with open(file_path, 'rb') as csvfile:
                    reader = csv.reader(csvfile, class_.OccurrencesDialect)
                    problems = validator.validate(reader)

                    if len(problems) > 0:
                        return False
                    else:
                        return True

