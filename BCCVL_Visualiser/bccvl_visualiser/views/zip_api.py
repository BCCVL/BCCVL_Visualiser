import logging
import tempfile
import mapscript
import zipfile
import os
import time
import hashlib

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

    @view_config(name='default')
    def auto_detect(self):
        log = logging.getLogger(__name__)
        log.debug('Processing view request in ZIP API v1')

        # Check if there's a data_url
        try:
            data_url = self.request.GET.getone('data_url')
        except:
            list = self.request.GET.getall('data_url_list')

        # Check if file_name was given, if none then assume multiple files
        try:
            file_name = self.request.GET.getone('file_name')
            return self.visualise_single_file(data_url, file_name)
        except:
            if data_url.endswith('.html.zip'):
                return self.visualise_html_zip(data_url)
            else:
                return self.visualise_multiple_layers(data_url)

    def visualise_single_file(self, data_url, file_name):
        log = logging.getLogger(__name__)


        log.debug('file_name: %s', file_name)

        new_data_url = None
        new_query = None
        new_filename = None
        return_url = None

        MyDataMover = FDataMover.get_data_mover_class()

        zip_file_path = MyDataMover.download(data_url=data_url, suffix='.zip')

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
                log.debug("new_data_url: %s", new_data_url)
                return_url = self.request.route_url('auto_detect_api_v1', traverse='/default', _query=new_query)
                # extract it
        fh.close()
        # delete the zip file
        log.debug("deleting the zip file")
        os.remove(zip_file_path)
        if return_url is not None:
            return HTTPFound(location=return_url)
        else:    
            return Response('Could not find the specified file in the zip.') 

    def visualise_multiple_layers(self, data_url):
        url_list = []

        log = logging.getLogger(__name__)

        MyDataMover = FDataMover.get_data_mover_class()

        # Download the zip file
        zip_file_path = MyDataMover.download(data_url=data_url, suffix='.zip')

        # Unzip the file
        fh = open(zip_file_path, 'rb')
        z = zipfile.ZipFile(fh)

        # Validate the files - make sure they end in .tif
        for name in z.namelist():
            if name.endswith('.tif') is False:
                return Response('This zip either does not have a flat file directory or have inconsistent file types.')

        # Extract
        for name in z.namelist():
            time_epoch = int(time.time() * 1000)

            (dirname, filename) = os.path.split(name)

            new_dirname =  str(time_epoch) + '_' + dirname

            extract_file_path = new_dirname + '/' + filename

            hash_string = hashlib.sha224(extract_file_path).hexdigest()
            new_filename = hash_string + ".tif"

            path = os.path.join(MyDataMover.MAP_FILES_DIR, new_filename)

            # write the file
            fd = open(path,"w")
            fd.write(z.read(name))
            fd.close()

            url_list.append(extract_file_path)

        log.debug("deleting the zip file")
        os.remove(zip_file_path)

        # Send it off to the raster api
        new_query = {'raster_list_url':url_list}
        url = self.request.route_url('raster_api_v1', traverse='/default', _query=new_query)
        return HTTPFound(location=url)

    def visualise_html_zip(self, data_url):
        MyDataMover = FDataMover.get_data_mover_class()

        # Download the zip file
        zip_file_path = MyDataMover.download(data_url=data_url, suffix='.zip')

        time_epoch = int(time.time() * 1000)
        dir_path = '/html_zip_' + str(time_epoch)
        os.mkdir(MyDataMover.PUBLIC_DIR + dir_path)

        fh = open(zip_file_path, 'rb')
        z = zipfile.ZipFile(fh)
        for name in z.namelist():
            dir_file_path = dir_path + '/' + name
            # write the file
            fd = open(MyDataMover.PUBLIC_DIR + dir_file_path, "w")
            fd.write(z.read(name))
            fd.close()

            if name.endswith('html'):
                index = dir_file_path

        os.remove(zip_file_path)

        new_data_url = self.request.application_url + '/public_data/' + index
        new_query = {'data_url': new_data_url}
        url = self.request.route_url('html_api_v1', traverse='/default', _query=new_query)

        return HTTPFound(location=url)

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(ZIPAPIViewv1, self).xmlrpc()

    def _to_dict(self):
        return ZIPAPIv1.to_dict()
