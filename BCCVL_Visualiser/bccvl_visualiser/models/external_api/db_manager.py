import logging
import os
import glob
import json


class DatabaseManager(object):

    USER = None
    PASSWORD = None
    PORT = None
    HOST = None
    DB_NAME = None
    MAP_FILES_DIR = None

    METADATA = {}

    @classmethod
    def configure_from_config(class_, settings):
        """ configure the DatabaseManager constants """
        log = logging.getLogger(__name__)

        if class_.is_configured():
            log.warn("Warning, %s is already configured. Ignoring new configuration.", str(class_))
            return

        class_.HOST = settings.get('bccvl.database_manager.host', None)
        class_.PORT = settings.get('bccvl.database_manager.port', None)
        class_.DB_NAME = settings.get('bccvl.database_manager.db_name', None)
        class_.USER = settings.get('bccvl.database_manager.user', None)
        class_.PASSWORD = settings.get('bccvl.database_manager.password', None)
        class_.MAP_FILES_DIR = settings.get('bccvl.mapscript.map_data_files_root_path', None)

        # Read in the metadata for each dataset
        for mdfile in glob.glob(os.path.join(class_.MAP_FILES_DIR, '*/layer_info.json')):
            mddata = json.load(open(mdfile, 'r'))
            for filename in mddata:
                class_.METADATA[filename] = mddata[filename]

    @classmethod
    def is_configured(cls):
        return cls.HOST is not None and cls.DB_NAME is not None and cls.PORT is not None and cls.USER is not None and cls.PASSWORD is not None

    @classmethod
    def connection_details(cls):
        return "user={} password={} dbname={} host={} port={}".format(cls.USER, cls.PASSWORD, cls.DB_NAME, cls.HOST, cls.PORT)

    @classmethod
    def update_metadata(cls, key, metadata):
        cls.METADATA[key] = metadata

    @classmethod
    def get_metadata(cls, key):
        return cls.METADATA.get(key, None)
