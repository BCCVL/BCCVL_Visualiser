import logging
import zope.interface
import bccvl_visualiser.invariants

class IDataMover(zope.interface.Interface):

    #: The base_url of the data mover
    BASE_URL = zope.interface.Attribute('The Base URL of the Data Mover (the API endpoint we will consume)')

    #: The Host ID we identify ourselves as to the Data Mover
    HOST_ID  = zope.interface.Attribute('The host we provide the Data Mover to identify us')

    #: The data_url of the file we're moving
    data_url = zope.interface.Attribute("The data_url that defines what we're moving")
    #: The data_id of the file we're moving
    data_id  = zope.interface.Attribute("The data_id that defines what we're moving")
    #: We should only have either the data_id or the data_url
    zope.interface.invariant(bccvl_visualiser.invariants.data_id_xor_data_url_invariant)

    #: The move job_id
    job_id   = zope.interface.Attribute("The move job id")

    #: The destination file path
    dest_file_path = zope.interface.Attribute("The destination of the file we're moving")

    def __init__(dest_file_path, data_id=None, data_url=None):
        """ The DataMover can be constructed from a data_id or a data_url (but not by both)
        """
        pass

    def _init_from_data_id(data_id):
        """ Init the the DataMover from a data_id """
        pass

    def _init_from_data_url(data_url):
        """ Init the the DataMover from a data_url """
        pass

    def move_file():
        """ Move the file locally """
        pass

    def get_status():
        """ Get the status of the current move """
        pass


class DataMover(object):
    zope.interface.implements(IDataMover)

    BASE_URL = None
    HOST_ID  = None

    @classmethod
    def configure_from_config(class_, settings):
        """ configure the DataMover constants """
        log = logging.getLogger(__name__)

        if (class_.BASE_URL is not None):
            log.warn("Warning, %s is already configured. Ignoring new configuration.", str(class_))
            return

        if (class_.HOST_ID is not None):
            log.warn("Warning, %s is already configured. Ignoring new configuration.", str(class_))
            return

        class_.BASE_URL = settings['bccvl.data_mover.base_url']
        class_.HOST_ID  = settings['bccvl.data_mover.host_id']

    def __init__(self, dest_file_path, data_id=None, data_url=None):
        """ initialise the map instance from a data_url """

        self.dest_file_path = dest_file_path
        self.job_id = None

        if data_id and data_url:
            raise ValueError("The DataMover API can't be provided a data_id and a data_url (there can be only one)")
        elif data_id:
            self._init_from_data_id(data_id)
        elif data_url:
            self._init_from_data_url(data_url)
        else:
            raise ValueError("A DataMover must be provided a data_id or a data_url.")

    def _init_from_data_id(self, data_id):
        self.data_id = data_id
        raise NotImplementedError("data_id is not yet supported")

    def _init_from_data_url(self, data_url):
        pass

    def move_file(self):
        pass

    def get_status(self):
        pass

class TestDataMover(DataMover):
    import requests

    # The dummy results will change based on what the data_url is

    @classmethod
    def configure_from_config(class_, settings):
        """ configure the DataMover constants """
        log = logging.getLogger(__name__)

        if (class_.BASE_URL is not None):
            log.warn("Warning, %s is already configured. Ignoring new configuration.", str(class_))
            return

        if (class_.HOST_ID is not None):
            log.warn("Warning, %s is already configured. Ignoring new configuration.", str(class_))
            return

        class_.BASE_URL = settings['bccvl.data_mover.base_url']
        class_.HOST_ID  = settings['bccvl.data_mover.host_id']

    def __init__(self, dest_file_path, data_id=None, data_url=None):
        """ initialise the map instance from a data_url """

        self.dest_file_path = dest_file_path
        self.job_id = None

        if data_id and data_url:
            raise ValueError("The DataMover API can't be provided a data_id and a data_url (there can be only one)")
        elif data_id:
            self._init_from_data_id(data_id)
        elif data_url:
            self._init_from_data_url(data_url)
        else:
            raise ValueError("A DataMover must be provided a data_id or a data_url.")

    def _init_from_data_id(self, data_id):
        self.data_id = data_id
        raise NotImplementedError("data_id is not yet supported")

    def _init_from_data_url(self, data_url):
        self.data_url = data_url

    def move_file(self):
        if ( self.job_id is None ):
            self.job_id = 1
            self._move_the_file()
            return { 'status': 'ACCEPTED', 'id': self.job_id }
        else:
            raise AssertionError("You can only move a file once per data mover instance")

    def get_status(self):
        if self.job_id:
            if self.status_code == 200:
                return { 'status': 'COMPLETE', 'id': self.job_id }
            else:
                return { 'status': 'FAILED', 'id': self.job_id }
        else:
            raise AssertionError("You can't get the status of a job that hasn't been started")

    def _move_the_file(self):
        """ Just get the file ourself """
        r = requests.get(self.data_url, verify=False)
        self.status_code = r.status_code

        dirname, filename = os.path.split(os.path.abspath(self.dest_file_path))

        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        # write the data from the url to the map file path
        output = open(self.dest_file_path,'wb')
        output.write(r.content)
        output.close()
