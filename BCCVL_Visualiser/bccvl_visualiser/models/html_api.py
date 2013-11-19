import mapscript
import os
import logging


from bccvl_visualiser.models import TextWrapper
from bccvl_visualiser.models.bccvl_map import *

from bccvl_visualiser.models.api import (
    BaseAPI
    )

import requests
import hashlib

class BaseHTMLAPI(BaseAPI):

    @staticmethod
    def identifier():
        return "html"

    @staticmethod
    def description():
        desc = """\
The HTML API is responsible for visualising \
general HTML files.\
"""
        return desc

class HTMLAPIv1(BaseHTMLAPI):
    """ v1 of the HTML API"""

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
        super(HTMLAPIv1, self).__init__(**kwargs)
