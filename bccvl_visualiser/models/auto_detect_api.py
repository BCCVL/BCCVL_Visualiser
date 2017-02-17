import mapscript
import os
import logging
import csv

from bccvl_visualiser.models.api import BaseAPI

class BaseAutoDetectAPI(BaseAPI):

    @staticmethod
    def identifier():
        return "auto_detect"

    @staticmethod
    def description():
        desc = """\
The AutoDetect API is responsible for determining \
what file has been provided, and redirecting to the appropriate API.\
"""
        return desc

class AutoDetectAPIv1(BaseAutoDetectAPI):
    """ v1 of the AutoDetect API"""

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
        super(AutoDetectAPIv1, self).__init__(**kwargs)


