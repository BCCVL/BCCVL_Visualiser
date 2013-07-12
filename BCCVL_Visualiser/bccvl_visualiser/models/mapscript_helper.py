import mapscript
import logging
import os

class MapScriptHelper(object):

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
    def get_map_and_ows_request_from_from_request(request, map_file_name):
        """ Returns a mapscript.mapObj and a mapscript.OWSRequest

            Given a request object, and optionally a map_file path,
            generates a mapObj and an OWSRequest object.

            The OWSRequest object will be generated using
            the request's query_string.

        """

        map_file_path = MapScriptHelper.get_map_file_path(request, map_file_name)
        map = mapscript.mapObj(map_file_path)

        ows_request = mapscript.OWSRequest()
        ows_request.loadParamsFromURL(request.query_string)

        return map, ows_request
