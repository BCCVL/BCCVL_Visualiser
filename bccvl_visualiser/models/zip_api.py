import mapscript
import os
import logging
import csv

from bccvl_visualiser.models.api import BaseAPI

class BaseZIPAPI(BaseAPI):

    @staticmethod
    def identifier():
        return "zip"

    @staticmethod
    def description():
        desc = """\
The ZIP API is responsible for unzip and \
redirecting file back to auto detect api.\
"""
        return desc

class ZIPAPIv1(BaseZIPAPI):
    """ v1 of the PNG API"""

    @staticmethod
    def version():
        return 1

    @classmethod
    def to_dict(_class):
        """ Returns a dict representation of the API

            This dict identifies the API, and its
            general purpose. More specific information about the
            API is defined at the specific version level of the API.
        """
        return_dict = {
            'name':         _class.identifier(),
            'description':  _class.description(),
            'version':      _class.version()
        }

        return return_dict

    def __init__(self, **kwargs):
        """ init the instance """
        super(ZIPAPIv1, self).__init__(**kwargs)
