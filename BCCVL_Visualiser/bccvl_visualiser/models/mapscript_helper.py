from mapscript import mapObj
import logging
import os
import threading

import requests
import hashlib

class BCCVLMap(mapObj):
    """ Our custom BCCVL mapObj.

        Provides additional utitlity functions on top of
        mapscript's mapObj class
    """


    EXTENSION = ""
    MAP_FILE_NAME = "default.map"

    def __init__(self, map_file_name=None, data_id=None, data_url=None, **kwargs):
        """ initialise the map instance from a data_url """
        if data_id and data_url:
            raise ValueError("A BCCVLMap can't have both a data_id and a data_url")
        elif data_id:
            self._init_from_data_id(data_id)
        elif data_url:
            self._init_from_data_url(data_url)
        else:
            raise ValueError("A BCCVLMap must have a data_id or a data_url")

        if map_file_name is None:
            map_file_name = self.__class__.MAP_FILE_NAME

        self.map_file_name = map_file_name
        self.map_file_path = MapScriptHelper.get_map_file_path(map_file_name)
        super(BCCVLMap, self).__init__(self.map_file_path, **kwargs)

    def _init_from_data_id(self, data_id):
        self.data_id = data_id
        raise NotImplementedError("data_id is not yet supported")

    def _init_from_data_url(self, data_url):
        """ initialise the map instance from a data_url """
        self.data_url = data_url

        # generate a hash of the url
        hash_string = hashlib.sha224(self.data_url).hexdigest()
        self.file_name = hash_string + self.__class__.EXTENSION

        self.data_file_path = self._download_data_to_file()

    def _download_data_to_file(self):
        r = requests.get(self.data_url, verify=False)
        r.raise_for_status()

        data_file_path = MapScriptHelper.get_path_to_map_data_file(self.file_name)
        dirname, filename = os.path.split(os.path.abspath(data_file_path))

        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        # write the data from the url to the map file path
        output = open(data_file_path,'wb')
        output.write(r.content)
        output.close()

        return data_file_path

class GeoTiffBCCVLMap(BCCVLMap):
    EXTENSION = ".tif"
    MAP_FILE_NAME = "default_geo_tiff.map"

class OccurrencesBCCVLMap(BCCVLMap):
    EXTENSION = ".csv"
    MAP_FILE_NAME = "default_occurrences.map"

class MapScriptHelper(object):

    MAPSCRIPT_RLOCK = threading.RLock()
    MAP_FILES_ROOT_PATH      = None
    MAP_DATA_FILES_ROOT_PATH = None

    @classmethod
    def configure_from_config(class_, settings):
        class_.MAP_FILES_ROOT_PATH      = settings['bccvl.mapscript.map_files_root_path']
        class_.MAP_DATA_FILES_ROOT_PATH = settings['bccvl.mapscript.map_data_files_root_path']

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

    @classmethod
    def set_data_for_map_layer_if_not_set(class_, map, data_id, layer_name):
        """ Given a data_id, will set the LAYER's DATA value

            Will speak to the Data Manager and get a local copy of the
            data (represented by the data_id). Once this is done,
            it will move the data to the map's SHAPEPATH.

            Once the data is in the right directory (SHAPEPATH), the
            DATA value for the LAYER will be set accordingly.

        """

        layer = map.getLayerByName(layer_name)

        if layer != None and layer.data == None:
                # TODO -> This is where we should talk to the data manager and
                # get access to the data file.
                raise NotImplementedError("TODO - This method needs to handle a data_id")


    @classmethod
    def get_map_and_ows_request_from_request(class_, query_string, map_file_name):
        """ Returns a mapscript.mapObj and a mapscript.OWSRequest

            Given a query_string, and optionally a map_file path,
            generates a mapObj and an OWSRequest object.

            The OWSRequest object will be generated using
            the query_string.

        """

        map_file_path = class_.get_map_file_path(map_file_name)
        map = mapscript.mapObj(map_file_path)

        class_._set_map_defaults_if_not_set(map)

        ows_request = mapscript.OWSRequest()

        log = logging.getLogger(__name__)

        ############################################
        #
        # NOTE / XXX / IMPORTANT
        #
        ############################################
        #
        # loadParamsFromURL causes a seg fault if passed an empty string.
        # Don't pass it an empty string...

        if query_string.strip() != '':
            ows_request.loadParamsFromURL(query_string)
        else:
            log.debug("Passed an empty query string, so skipping OWSRequest.loadParamsFromURL")


        return map, ows_request

    @classmethod
    def _set_map_defaults_if_not_set(class_, map):
        log = logging.getLogger(__name__)

        map_data_files_root_path = class_.MAP_DATA_FILES_ROOT_PATH

        if map.shapepath == None:
            log.debug("Setting mapObj.shapepath as not already set. Set to: %s", map_data_files_root_path)
            map.shapepath = map_data_files_root_path

