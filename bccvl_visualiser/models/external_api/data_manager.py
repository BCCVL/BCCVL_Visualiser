import logging

class DataManager(object):

    BASE_URL = None

    @classmethod
    def configure_from_config(class_, settings):
        """ configure the DataManager constants """
        log = logging.getLogger(__name__)

        if (class_.BASE_URL is not None):
            log.warn("Warning, %s is already configured. Ignoring new configuration.", str(class_))
            return

        class_.BASE_URL = settings['bccvl.data_manager.base_url']

    def __init__(self, data_id=None, data_url=None):
        """ initialise the DataManager from a data_id or data_url """

        if data_id and data_url:
            raise ValueError("The DataManager API can't be provided a data_id and a data_url (there can be only one)")
        elif data_id:
            self._init_from_data_id(data_id)
        elif data_url:
            self._init_from_data_url(data_url)
        else:
            raise ValueError("A DataManager must be provided a data_id or a data_url.")

    def _init_from_data_id(self, data_id):
        self.data_id = data_id
        raise NotImplementedError("data_id is not yet supported")

    def _init_from_data_url(self, data_url):
        self.data_url = data_url
        raise NotImplementedError("data_url is not yet supported")
