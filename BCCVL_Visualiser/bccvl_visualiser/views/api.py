import logging
import os
import datetime
import subprocess
import shlex
import zipfile
import json
from osgeo import gdal, ogr

from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from sqlalchemy.exc import DBAPIError

from bccvl_visualiser.models import (
    APICollection
    )

from bccvl_visualiser.views import BaseView
from bccvl_visualiser.utils import FetchJob, fetch_file, data_dir
from concurrent.futures import ThreadPoolExecutor
from bccvl_visualiser.models.external_api import DatabaseManager

LOG = logging.getLogger(__name__)

def fetch_worker(request, data_url, job):
    # get location of local data file
    job.update(status=FetchJob.STATUS_IN_PROGRESS, start_timestamp=datetime.datetime.now())
    try:
        loc = fetch_file(request, data_url)
        install_to_db = request.params.get('INSTALL_TO_DB', False)

        # Check the dataset is to be imported to database server
        if install_to_db:
            layer_mappings = request.params.get('LAYER_MAPPING', None)
            base_layer = request.params.get('BASE_LAYER', None)
            if layer_mappings is None or base_layer is None:
                raise Exception("No layer/table mappings or base layer is specified")

            datadir, filename = os.path.split(loc)
            fname, fext = os.path.splitext(filename)
            if fext == '.zip':
                # Check if shape file exists. If so, already unzip.
                with zipfile.ZipFile(loc, 'r') as zipf:
                    zipf.extractall(datadir)

            # Import dataset to postgis server
            schemaname = None
            if DatabaseManager.is_configured():
                # TODO: To support other file type?
                if os.path.isfile(os.path.join(datadir, fname + ".shp")):
                    dbFilename = os.path.join(datadir, fname + ".shp")
                elif os.path.isdir(os.path.join(datadir, fname + ".gdb")):
                    dbFilename = os.path.join(datadir, fname + ".gdb")
                else:
                    raise Exception("Unsupported dataset type")
                schemaname = fname.replace('.', '_').replace('-', '_').lower()
                import_into_db(dbFilename, schemaname)

            # write the layer mapping info as metadata.
            write_dataset_metadata(layer_mappings, base_layer, schemaname, dbFilename)
                
        job.update(status=FetchJob.STATUS_COMPLETE, end_timestamp=datetime.datetime.now())
    except Exception as e:
        reason = 'Failed to fetch data from {0}. {1}'.format(data_url, str(e))
        LOG.warning(reason)
        job.update(status=FetchJob.STATUS_FAILED, end_timestamp=datetime.datetime.now(), reason=reason)


def write_dataset_metadata(layer_mappings, blayer, schemaname, filepath):
    # Metadata about mapping layer name to a table from the request params 
    # i.e. layername1:tablename1,layername2:tablename2
    # base_layer is the table-name:common-column
    datadir, filename = os.path.split(filepath)
    mappings = dict(item.split(':') for item in layer_mappings.split(','))
    # Use filename as schema
    for k in mappings:
        mappings[k] = schemaname + '.' + mappings[k]

    base_layer, common_col = blayer.split(':')
    layer_md = { 'base_layer' : base_layer,
                 'common_column': common_col,
                 'layer_mappings' : mappings,
                 'id_column': 'fid',
                 'geometry_column': 'geom'
                }

    # dataset only has extent if it has geometry column.
    extent = get_Extent_from(base_layer)
    if extent:
        xmin, xmax, ymin, ymax = extent
        layer_md['base_extent'] = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}

    jsonfile = open(os.path.join(datadir, "layer_mappings.json"), 'w')
    json.dump(layer_md, jsonfile, indent=4)
    jsonfile.close()

def get_Extent_from db(tablename):
    # Get extent of the table specified from DB server
    command = 'PG:{dbconn}'.format(dbconn=DatabaseManager.connection_details())
    dbconn = ogr.Open(command)
    layerdata = dbconn.ExecuteSQL("select * from {table}".format(table=tablename))
    extent = None
    if len(layerdata.GetGeometryColumn()) > 0:
        extent = layerdata.GetExtent()
    dbconn.Destroy()
    return extent

def import_into_db(dbfname, schemaname):
    # Import dataset into db server
    try:
        # create schema
        command = 'ogrinfo -so PG:"{dbconn}" -sql "create schema if not exists {schema}"'.format(dbconn=DatabaseManager.connection_details(), schema=schemaname)
        p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        if p.returncode != 0:
            raise Exception("Fail to create schema '{}'. {}".format(schemaname, err))
            
        # import the dataset. Set FID and geometry name.
        command = 'ogr2ogr -f PostgreSQL PG:"{dbconn}" -lco schema={schema} -lco FID=fid -lco GEOMETRY_NAME=geom  {dbfile} -skipfailures'.format(dbconn=DatabaseManager.connection_details(), schema=schemaname, dbfile=dbfname)
        p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        if p.returncode != 0:
            raise Exception("Fail to import dataset '{}. {}'".format(dbfname, err))

    except Exception as e:
        raise Exception("Failed to import dataset into DB server. {0}".format(str(e)))


@view_defaults(route_name='api')
class ApiCollectionView(BaseView):
    """The API level view"""

    _executor = ThreadPoolExecutor(max_workers=3)
    _fetch_jobs = {}

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(ApiCollectionView, self).json()

    @view_config(name='.text')
    def text(self):
        return super(ApiCollectionView, self).text()

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(ApiCollectionView, self).xmlrpc()

    @view_config(name='fetch', renderer='json')
    def fetch(self):
        """This is a fetch endpoint to fetch data from the data url specified.

        This endpoint requires an additional WMS parameter
        DATA_URL. The DATA_URL, should point to a downloadable file
        which can be used as raster data input for mapserver.
        """

        LOG.debug('Processing ows request')

        data_url = None
        try:
            data_url = self.request.GET.getone('DATA_URL')
        except:
            LOG.warn('No data_url provided')
            data_url = None
            return self.StatusResponse(FetchJob.STATUS_FAILED, 'No data_url provided')


        # Check if a job has been submitted or data has been dowbloaded for this data url.
        datadir = data_dir(self.request, data_url)
        job = self._fetch_jobs.get(datadir)
        if job:
            reason = job.reason
            status = job.status
            if job.status in (FetchJob.STATUS_FAILED, FetchJob.STATUS_COMPLETE):
                del self._fetch_jobs[datadir]
            return self.StatusResponse(status, reason)
        elif os.path.exists(datadir):
            return self.StatusResponse(FetchJob.STATUS_COMPLETE)

        # Submit a new fetch job with datadir as job ID.
        job = FetchJob(datadir)
        self._fetch_jobs[datadir] = job
        self._executor.submit(fn=fetch_worker, request=self.request, data_url=data_url, job=job)
        return self.StatusResponse(job.status, job.reason)


    def _to_dict(self):
        return APICollection.to_dict()

    def StatusResponse(self, status, reason=None):
        return {'status': status, 'reason': reason}
