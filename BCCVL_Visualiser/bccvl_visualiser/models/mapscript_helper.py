import mapscript
import logging
import os
import threading


class MapScriptHelper(object):

    MAPSCRIPT_RLOCK = threading.RLock()

    @staticmethod
    def get_path_to_map_data_file(request, data_file_name):
        log = logging.getLogger(__name__)

        settings = request.registry.settings
        map_data_files_root_path = settings['bccvl.mapscript.map_data_files_root_path']

        return_value = os.path.join(map_data_files_root_path, data_file_name)

        log.debug('Map data files root path: %s', map_data_files_root_path)
        log.debug('Map data file path: %s', return_value)

        return return_value

    @staticmethod
    def get_map_file_path(request, map_file_name):
        """ Returns the full os system path to the mapfile

            Uses the application config (found in request.registry.settings),
            to look up the root map files path (where the map files are stored),
            and then joins this with the provided map_file_name argument.

        """

        log = logging.getLogger(__name__)

        settings = request.registry.settings
        map_files_root_path = settings['bccvl.mapscript.map_files_root_path']

        return_value = os.path.join(map_files_root_path, map_file_name)

        log.debug('Map files root path: %s', map_files_root_path)
        log.debug('Map file path: %s', return_value)

        return return_value

    @staticmethod
    def set_data_for_map_layer_if_not_set(map, data_id, layer_name):
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


    @staticmethod
    def get_map_and_ows_request_from_request(request, map_file_name):
        """ Returns a mapscript.mapObj and a mapscript.OWSRequest

            Given a request object, and optionally a map_file path,
            generates a mapObj and an OWSRequest object.

            The OWSRequest object will be generated using
            the request's query_string.

        """

        map_file_path = MapScriptHelper.get_map_file_path(request, map_file_name)
        map = mapscript.mapObj(map_file_path)

        MapScriptHelper._set_map_defaults_if_not_set(request, map)

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

        if request.query_string.strip() != '':
            ows_request.loadParamsFromURL(request.query_string)
        else:
            log.debug("Passed an empty query string, so skipping OWSRequest.loadParamsFromURL")


        return map, ows_request

    @staticmethod
    def _set_map_defaults_if_not_set(request, map):
        log = logging.getLogger(__name__)

        settings = request.registry.settings
        map_data_files_root_path = settings['bccvl.mapscript.map_data_files_root_path']

        if map.shapepath == None:
            log.debug("Setting mapObj.shapepath as not already set. Set to: %s", map_data_files_root_path)
            map.shapepath = map_data_files_root_path

