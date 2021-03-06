import mapscript
import os
import logging
import csv

from bccvl_visualiser.models.api import BaseAPI

class BaseRAPI(BaseAPI):

    @staticmethod
    def identifier():
        return "r"

    @staticmethod
    def description():
        desc = """\
The R API is responsible for visualising \
R files.\
"""
        return desc

class RAPIv1(BaseRAPI):
    """ v1 of the R API"""

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
        super(RAPIv1, self).__init__(**kwargs)


