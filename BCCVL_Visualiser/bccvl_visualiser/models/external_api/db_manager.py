import logging

class DatabaseManager(object):

    USER = None
    PASSWORD = None
    PORT = None
    HOST = None
    DB_NAME = None

    @classmethod
    def configure_from_config(class_, settings):
        """ configure the DatabaseManager constants """
        log = logging.getLogger(__name__)

        if class_.is_configured():
            log.warn("Warning, %s is already configured. Ignoring new configuration.", str(class_))
            return

        class_.HOST = settings['bccvl.database_manager.host']
        class_.PORT = settings['bccvl.database_manager.port']
        class_.DB_NAME = settings['bccvl.database_manager.db_name']
        class_.USER = settings['bccvl.database_manager.user']
        class_.PASSWORD = settings['bccvl.database_manager.password']

    @classmethod
    def is_configured(cls):
        return cls.HOST is not None and cls.DB_NAME is not None and cls.PORT is not None and cls.USER is not None and cls.PASSWORD is not None

    @classmethod
    def connection_details(cls):
        return "user={} password={} dbname={} host={} port={}".format(cls.USER, cls.PASSWORD, cls.DB_NAME, cls.HOST, cls.PORT)
