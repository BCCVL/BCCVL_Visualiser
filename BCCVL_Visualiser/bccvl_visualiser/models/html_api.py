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

    @classmethod
    def replace_urls(_class, in_str, data_url):
        ''' A HACK to reroute all the image references back to plone
        '''

        def replace_img_src_url(match_obj):
            # example data_url: 
            # http://compute.bccvl.org.au/experiments/bioclim-unthemed/bioclim-unthemed-result-2013-11-20t00-47-41-120241/results.html/view/++widget++form.widgets.file/@@download/results.html
            current_data_url_file_name_match = re.search(r'[^/]+$', data_url)
            # would produce results.html
            current_data_url_file_name = current_data_url_file_name_match.group(0)

            # example: 'AUC.png'
            relative_url = match_obj.group(2)

            # Replace all instances of current_data_url_file_name with relative_url
            # results.html with AUC.png
            absolute_url = data_url.replace(current_data_url_file_name, relative_url)
            return 'src="%s"' % absolute_url

        image_src_search_regex = r'src=([\'"])([^/].+?)\1'
        # Call our replace_url for every match in in_str
        out_str = re.sub(image_src_search_regex, replace_img_src_url, in_str)

        return out_str

