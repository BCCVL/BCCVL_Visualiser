import logging
import tempfile
import mapscript
import zipfile
import os
import time

from pyramid.response import Response, FileResponse
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from sqlalchemy.exc import DBAPIError

from bccvl_visualiser.models import BaseZIPAPI, ZIPAPIv1, FDataMover
from bccvl_visualiser.views import BaseView

@view_defaults(route_name='zip_api')
class BaseZIPAPIView(BaseView):
    """The Base ZIP API level view '/api/zip'"""

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(BaseZIPAPIView, self).json()

    @view_config(name='.text')
    def text(self):
        return super(BaseZIPAPIView, self).text()

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(BaseZIPAPIView, self).xmlrpc()

    def _to_dict(self):
        return_dict = {str(k): str(v) for k, v in BaseZIPAPI.get_human_readable_inheritors_version_dict().items()}
        return return_dict

@view_defaults(route_name='zip_api_v1')
class ZIPAPIViewv1(BaseZIPAPIView):

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(ZIPAPIViewv1, self).json()

    @view_config(name='.text')
    def text(self):
        return super(ZIPAPIViewv1, self).text()

    @view_config(name='data_url_view')
    @view_config(name='default')
    def view(self):
        log = logging.getLogger(__name__)
        log.debug('Processing view request in ZIP API v1')

        data_url = self.request.GET.getone('data_url')
        file_name = self.request.GET.getone('file_name')
        log.debug('file_name: %s', file_name)

        new_data_url = None
        new_query = None
        new_filename = None

        MyDataMover = FDataMover.get_data_mover_class()
        content = None

        zip_file_path = MyDataMover.download(data_url=data_url, suffix='.zip')
        log.debug('File path: %s', zip_file_path)
        log.debug('public dir: %s', MyDataMover.PUBLIC_DIR)

        fh = open(zip_file_path, 'rb')
        z = zipfile.ZipFile(fh)
        for name in z.namelist():
            if name == file_name:
                # epoch timestamp for unique filename
                time_epoch = int(time.time() * 1000)


                (dirname, filename) = os.path.split(name)

                new_dirname =  str(time_epoch) + '_' + dirname
                os.mkdir(MyDataMover.PUBLIC_DIR + '/' + new_dirname)
                log.debug("directory to extract: %s", new_dirname)

                extract_file_path = new_dirname + '/' + filename

                # write the file
                fd = open(MyDataMover.PUBLIC_DIR + '/' + extract_file_path,"w")
                fd.write(z.read(name))
                fd.close()

                log.debug("finished writing file")

                # Prepare url and query to return it to auto detect                
                new_data_url = self.request.application_url + '/public_data/' + extract_file_path
                new_query = {'data_url':new_data_url}
                url = self.request.route_url('auto_detect_api_v1', traverse='/default', _query=new_query)
                return HTTPFound(location=url)
                # extract it
        fh.close()
        # delete the zip file
        os.remove(zip_file_path)

        return Response('Could not find the specified file in the zip.')

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(ZIPAPIViewv1, self).xmlrpc()

    def _to_dict(self):
        return ZIPAPIv1.to_dict()
