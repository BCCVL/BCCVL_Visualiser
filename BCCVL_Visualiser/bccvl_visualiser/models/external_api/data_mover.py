import logging
import os
import time
import requests
import random
import zope.interface
import bccvl_visualiser.invariants
import tempfile
from contextlib import contextmanager
import xmlrpclib

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

class FDataMover(object):
    local = False

    @classmethod
    def new_data_mover(_class, *args, **kwargs):
        """ Create a data mover """

        if _class.local:
            return LocalDataMover(*args, **kwargs)
        else:
            return DataMover(*args, **kwargs)

    @classmethod
    def get_data_mover_class(_class, *args, **kwargs):
        """ Get the class of data mover that the factory would instantiate for you """

        if _class.local:
            return LocalDataMover
        else:
            return DataMover

class DataMover(object):
    zope.interface.implements(IDataMover)

    BASE_URL = None
    HOST_ID  = None

    COMPLETE_STATUS = 'COMPLETED'
    REJECTED_STATUS = 'REJECTED'
    PENDING_STATUS  = 'PENDING'
    FAILED_STATUS   = 'FAILED'

    # The time to sleep between data mover checks
    SLEEP_BETWEEN_DATA_MOVER_CHECKS = 2

    @classmethod
    @contextmanager
    def open(class_, **kwargs):
        """ Open a file using the data mover, yield it, and then delete it.
        """

        # Create a tempfile to store the R file
        tf = tempfile.NamedTemporaryFile(delete=False, prefix='data_mover_')
        file_path = tf.name

        try:
            # create a mover to get the file
            mover = class_(file_path, **kwargs)
            mover.move_and_wait_for_completion()

            # open the tempfile
            with open(file_path, 'r') as f:
                # yield the file
                yield f
        finally:
            # remove the tempfile
            os.remove(file_path)

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
        self.job_id   = None
        self.data_url = None
        self.data_id  = None

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

    @classmethod
    def get_xmlrpc_url(class_):
        return (class_.BASE_URL + "/" + "data_mover")

    def move_file(self):
        _class = self.__class__
        if self.data_url:
            source_dict = { 'type':'url', 'url': self.data_url }
            dest_dict   = { 'type':'scp', 'host':_class.HOST_ID, 'path':self.dest_file_path }

            s = xmlrpclib.ServerProxy(_class.get_xmlrpc_url())
            response = s.move(source_dict, dest_dict)

            if response['status'] == _class.PENDING_STATUS:
                self.job_id = response['id']
            return response
        else:
            raise NotImplementedError("move_file for data_id is not yet supported")

    def get_status(self):
        _class = self.__class__
        s = xmlrpclib.ServerProxy(_class.get_xmlrpc_url())
        response = s.check_move_status(self.job_id)
        return response

    def move_and_wait_for_completion(self):
        """ Wait for the move to complete.

            Raises IOError if move fails.
            Returns move job status (result of get_status) if job succeeds.
        """

        log = logging.getLogger(__name__)

        _class = self.__class__
        response = self.move_file()
        log.info("move response: %s", response)
        if response['status'] == _class.REJECTED_STATUS:
            raise IOError("Move Failed (rejected): %s" % response['reason'])

        while True:
            response = self.get_status()
            log.info("get_status response: %s", response)
            if response['status'] == _class.FAILED_STATUS:
                # if the move failed, raise an exception
                raise IOError("Move Failed (failed during move): %s" % response['reason'])
            elif response['status'] == _class.COMPLETE_STATUS:
                # if the move is complete, return the status
                return response
            else:
                # it's in progress, so wait
                time.sleep(_class.SLEEP_BETWEEN_DATA_MOVER_CHECKS)

class LocalDataMover(DataMover):

    def move_file(self):
        if ( self.job_id is None ):
            self.job_id = random.randint(1,1000000)
            self._move_the_file()
            return { 'status': self.__class__.PENDING_STATUS, 'id': self.job_id }
        else:
            raise AssertionError("You can only move a file once per data mover instance")

    def get_status(self):
        if self.job_id:
            if self.status_code == 200:
                return { 'status': self.__class__.COMPLETE_STATUS, 'id': self.job_id }
            else:
                return {
                    'status': self.__class__.FAILED_STATUS,
                    'reason': 'Bad HTTP status code: %s' % self.status_code,
                    'id': self.job_id
                }
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
