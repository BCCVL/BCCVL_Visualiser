import mapscript
import csv
from mapscript import mapObj, OWSRequest
import logging
import os
import threading
import sys

import hashlib

from bccvl_visualiser.models.external_api.data_mover import FDataMover

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
        """ configure the BCCVL Map constants """
        log = logging.getLogger(__name__)

        if (class_.MAP_FILES_ROOT_PATH is not None) or (class_.MAP_DATA_FILES_ROOT_PATH is not None):
            log.warn("Warning, %s is already configured. Ignoring new configuration.", str(class_))
            return

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
            raise ValueError("A BCCVLMap must have a data_id or a data_url.")

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
            log.debug("Setting OWS paramater LAYER as not already set. Set to: %s", self.layer_name)

        if (ows_request.getValueByName('LAYERS') is None):
            ows_request.addParameter('LAYERS', self.layer_name)
            log.debug("Setting OWS paramater LAYERS as not already set. Set to: %s", self.layer_name)

        self.ows_request = ows_request

    def _download_data_to_file(self):
        mover = FDataMover.new_data_mover(self.data_file_path, data_url = self.data_url)

        # Make sure only one thread is trying to check for
        # the existance of, or trying to write the file
        # at any time.
        with self.__class__.MAPSCRIPT_RLOCK:
            mover.move_and_wait_for_completion()

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
        """ Render this map object

            This will inspect the OWS request type, and render the correct image
            for the request.

            Known supported OWS REQUEST values:

            * GetLegendGraphic: Will render the legend for the OWS request
            * GetMap: Will render the map tile for the OWS request
        """

        log = logging.getLogger(__name__)

        content = None          # the bytes of the rendered image
        content_type = None     # the image mimetype
        retval = None           # the OWS return value, useful for debugging

        with self.__class__.MAPSCRIPT_RLOCK:
            try:
                ows_request_type = self.ows_request.getValueByName('REQUEST')

                if (ows_request_type == 'GetLegendGraphic'):
                    # Draw the legend for the map
                    retval = self.loadOWSParameters(self.ows_request)
                    image = self.drawLegend()
                    content = image.getBytes()
                    content_type = image.format.mimetype
                elif (ows_request_type == 'GetMap'):
                    # Draw the map (tiles)
                    retval = self.loadOWSParameters(self.ows_request)
                    image = self.draw()
                    content = image.getBytes()
                    content_type = image.format.mimetype
                else:
                    # Unexpected OWS request. Do our best to support it by
                    # falling back to using the OWS Dispatch

                    # Tell mapscript to start capturing the stdout in a buffer
                    mapscript.msIO_installStdoutToBuffer()
                    # dispatch the OWS request
                    retval = self.OWSDispatch(self.ows_request)
                    # Get the content type of the return value
                    content_type = mapscript.msIO_stripStdoutBufferContentType()
                    # Get the content of the resulting image
                    content = mapscript.msIO_getStdoutBufferBytes()

                if retval != mapscript.MS_SUCCESS:
                    # Failed to render the desired image
                    raise RuntimeError("Failed to render map OWS request")

            except:
                log.error("Error while trying to render map: %s", sys.exc_info()[0])
                raise
            finally:
                # Reset the mapscript I/O pointers back to where they should be
                mapscript.msIO_resetHandlers()

        return content, content_type, retval

class GeoTiffBCCVLMap(BCCVLMap):
    EXTENSION = ".tif"
    DEFAULT_MAP_FILE_NAME = "default_raster.map"

    def __init__(self, **kwargs):
        super(GeoTiffBCCVLMap, self).__init__(**kwargs)

    def _set_map_defaults_if_not_set(self, **kwargs):
        """ Default the map's attributes """
        super(GeoTiffBCCVLMap, self)._set_map_defaults_if_not_set(**kwargs)

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

        lng_column = 'lon'
        lat_column = 'lat'

        valid, problems = self.__class__._check_if_occurrences_csv_valid(self.data_file_path, lng=lng_column, lat=lat_column)
        if not valid:
            # Delete the file
            os.remove(self.data_file_path)
            raise ValueError("Problem parsing Occurrence/Absences CSV file. Problems: %s" % (problems))

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
    def _check_if_occurrences_csv_valid(class_, file_path, lng='lon', lat='lat', limit=10):
        log = logging.getLogger(__name__)

        field_names = []
        problems = []

        with class_.MAPSCRIPT_RLOCK:
            with open(file_path, 'rb') as csvfile:
                reader = csv.reader(csvfile, class_.OccurrencesDialect)
                field_names = reader.next()

                # Ensure that the expected latitude and longitude columns are in the
                # list of expected field_names
                if not (lng in field_names):
                    log.warn("CSV (%s) doesn't contain a '%s' column", file_path, lng)
                    problems.append("CSV (%s) doesn't contain a '%s' column" % (file_path, lng))
                if not (lat in field_names):
                    problems.append("CSV (%s) doesn't contain a '%s' column" % (file_path, lat))
                    log.warn("CSV (%s) doesn't contain a '%s' column", file_path, lat)

                lng_position = field_names.index(lng)
                lat_position = field_names.index(lat)

                num_cols = len(field_names)

                # Iterate over each remaining row in the csv reader (we've already processed
                # the header)
                for row in reader:
                    # Check that the row has the correct number of columns
                    if len(row) != num_cols:
                        problems.append("CSV (%s) contains different length rows: %s" % (file_path, rows))

                    # Check that the row has a valid lng
                    lng_s = row[lng_position]
                    try:
                        lng_f = float(lng_s)
                    except:
                        problems.append("CSV (%s) contains an invalid %s: %s" % (file_path, lng, lng_s))

                    # Check that the row has a valid lat
                    lat_s = row[lat_position]
                    try:
                        lat_f = float(lat_s)
                    except:
                        problems.append("CSV (%s) contains an invalid %s: %s" % (file_path, lat, lat_s))

                    # Only provide info on at most +limit+ problems
                    if limit and ( len(problems) >= limit ):
                        break

        valid = ( len(problems) == 0 )
        return valid, problems
