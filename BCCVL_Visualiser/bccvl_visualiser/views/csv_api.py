import logging
import tempfile
import mapscript
import requests
import csv
import tempfile
import os

from pyramid.response import Response, FileResponse
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid_xmlrpc import *

from sqlalchemy.exc import DBAPIError

from bccvl_visualiser.models import CSVAPIv1, DataMoverF, BaseCSVAPI
from bccvl_visualiser.views import BaseView

@view_defaults(route_name='csv_api')
class BaseCSVAPIView(BaseView):
    """The Base CSV API level view '/api/csv'"""

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(BaseCSVAPIView, self).json()

    @view_config(name='.text')
    def text(self):
        return super(BaseCSVAPIView, self).text()

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(BaseCSVAPIView, self).xmlrpc()

    def _to_dict(self):
        return_dict = {str(k): str(v) for k, v in BaseCSVAPI.get_human_readable_inheritors_version_dict().items()}
        return return_dict

@view_defaults(route_name='csv_api_v1')
class CSVAPIViewv1(BaseCSVAPIView):

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(CSVAPIViewv1, self).json()

    @view_config(name='.text')
    def text(self):
        return super(CSVAPIViewv1, self).text()

    @view_config(name='data_url_view', renderer='../templates/api/csv/v1/view.pt')
    @view_config(name='default', renderer='../templates/api/csv/v1/view.pt')
    def view(self):

        log = logging.getLogger(__name__)
        log.debug('Processing view request in CSV API v1')

        data_url = self.request.GET.getone('data_url')

        tf = tempfile.NamedTemporaryFile(delete=False, prefix='csv_view_v1_', suffix='.csv')
        file_path = tf.name

        # create a mover to get the CSV file
        mover = DataMoverF.new_data_mover(file_path, data_url = data_url)
        mover.move_and_wait_for_completion()

        out_str = '<table>'

        with open(file_path, 'rb') as csvfile:

            # TODO: Change this to use list comprehension, or to process the csv file in
            # the template.
            first = True
            for row in csv.reader(csvfile):
                if first:
                    out_str = out_str + "<thead>"
                    out_str = out_str + "<tr>"
                    for el in row:
                        out_str = ( out_str + "<th>" + el + "</th>" )
                    out_str = out_str + "</tr>"
                    out_str = out_str + "</thead><tbody>"
                    first = False
                else:
                    out_str = out_str + "<tr>"
                    for el in row:
                        out_str = ( out_str + "<td>" + el + "</td>" )
                    out_str = out_str + "</tr>"

            out_str = out_str + '</tbody></table>'

        # Don't forget to clean up at the end
        os.remove(file_path)
        return { 'file_content': out_str }

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(CSVAPIViewv1, self).xmlrpc()

    def _to_dict(self):
        return CSVAPIv1.to_dict()
