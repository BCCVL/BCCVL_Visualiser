import logging

class DataManager(object):

    BASE_URL = None

    @classmethod
    def configure_from_config(class_, settings):
        """ configure the BCCVL Map constants """
        log = logging.getLogger(__name__)

        if (class_.BASE_URL is not None):
            log.warn("Warning, %s is already configured. Ignoring new configuration.", str(class_))
            return

        class_.BASE_URL = settings['bccvl.data_manager.base_url']

    def __init__(self):
        pass
