import logging
import os
import datetime
import subprocess
import shlex
import zipfile
import json
import glob
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
                # Check for shape file, then for gdb directories
                dbFiles = [dbfile for dbfile in glob.glob(os.path.join(datadir, fname, 'data/*.dbf'))]
                if len(dbFiles) == 0:
                    dbFiles = [dbfile for dbfile in glob.glob(os.path.join(datadir, fname, 'data/*.gdb'))]
                if len(dbFiles) == 0:
                    raise Exception("Unsupported dataset type")

                # Import each df file into database
                metadata = {}
                for dbFilename in dbFiles:
                    dbfname = os.path.basename(dbFilename)

                    # Skip this db file if it has been imported before
                    #if DatabaseManager.get_metadata(filename) is not None:
                    #    continue

                    # Import db file into the database
                    schemaname = fname.replace('.', '_').replace('-', '_').lower()
                    import_into_db(dbFilename, schemaname)

                    # get the layer info as metadata.
                    md = get_dataset_metadata(schemaname, dbFilename)
                    metadata[dbfname] = md
                    #metadata.update(md)

                    # update the metadata stored in DatabaseManager
                    DatabaseManager.update_metadata(dbfname, md)

                # Save the metadata as json file for loading when visualiser start
                jsonfile = open(os.path.join(datadir, "layer_info.json"), 'w')
                json.dump(metadata, jsonfile, indent=4)
                jsonfile.close()   

        job.update(status=FetchJob.STATUS_COMPLETE, end_timestamp=datetime.datetime.now())
    except Exception as e:
        reason = 'Failed to fetch data from {0}. {1}'.format(data_url, str(e))
        LOG.warning(reason)
        job.update(status=FetchJob.STATUS_FAILED, end_timestamp=datetime.datetime.now(), reason=reason)


def get_dataset_metadata(schemaname, filepath):
    # list of table names for the given db file
    tablenames = get_tablenames(filepath)

    # Get info about the table
    metadata = {}
    for name in tablenames:
        tablename = schemaname + '.' + name.lower()
        extent, fieldnames = get_layerinfo_from_db(tablename)

        md = { 'table' : tablename,
               'fields' : fieldnames,
               'id_column': 'fid'
             }

        # dataset only has extent if it has geometry column.
        if extent:
            xmin, xmax, ymin, ymax = extent
            md['base_extent'] = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}
            md['geometry_column'] = 'geom'
        metadata[name.lower()] = md
    return metadata

def get_layerinfo_from_db(tablename):
    # Get extent of the table specified from DB server
    command = 'PG:{dbconn}'.format(dbconn=DatabaseManager.connection_details())
    dbconn = ogr.Open(command)
    #layerdata = dbconn.ExecuteSQL("select * from {table}".format(table=tablename))
    layerdata =dbconn.GetLayer(str(tablename))

    # Get a list of user defined column names
    layerdefn = layerdata.GetLayerDefn()
    fieldnames = [layerdefn.GetFieldDefn(i).GetName() for i in range(layerdefn.GetFieldCount())]

    extent = None
    if len(layerdata.GetGeometryColumn()) > 0:
        extent = layerdata.GetExtent()
    dbconn.Destroy()
    return extent, fieldnames

def import_into_db(dbfname, schemaname):
    # Import dataset into db server
    try:
        # create schema
        command = 'ogrinfo -so PG:"{dbconn}" -sql "create schema if not exists {schema}"'.format(dbconn=DatabaseManager.connection_details(), schema=schemaname)
        p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        if p.returncode != 0 or len(err) > 0:
            raise Exception("Fail to create schema '{}'. {}".format(schemaname, err))
            
        # import the dataset. Set FID and geometry name.
        command = 'ogr2ogr -f PostgreSQL PG:"{dbconn}" -lco schema={schema} -lco FID=fid -lco GEOMETRY_NAME=geom  {dbfile} -skipfailures -overwrite --config PG_USE_COPY YES'.format(dbconn=DatabaseManager.connection_details(), schema=schemaname, dbfile=dbfname)
        p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        if p.returncode != 0 or len(err) > 0:
            raise Exception("Fail to import dataset '{}. {}'".format(dbfname, err))

    except Exception as e:
        raise Exception("Failed to import dataset into DB server. {0}".format(str(e)))

def get_tablenames(dbfname):
    command = "ogrinfo -so -q {filename}".format(filename=dbfname)
    p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    if p.returncode != 0 or len(err) > 0:
        raise Exception("Fail to get table names from '{}': {}".format(dbfname, err))

    # parse for tablenames. 
    # output format: 1: tablename1 (None) \n\r2: tablename2 (polygon) \n\r3:
    tokens = output.split(":")
    names = [tokens[i].split()[0].strip() for i in range(1, len(tokens))]
    return names

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
