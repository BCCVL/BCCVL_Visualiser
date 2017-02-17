import fcntl
import fnmatch
import hashlib
import logging
import mimetypes
import os
import os.path
import shutil
import urlparse
import zipfile

import gdal
from org.bccvl import movelib

from bccvl_visualiser.auth import update_auth_cookie

LOG = logging.getLogger(__name__)

# TODO: replace existing DataMover classes with a configurable utility to remove
#       bccvl specific code from visualiser


class LockFile(object):

    def __init__(self, path):
        self.path = path
        self.fd = None

    def acquire(self, timeout=None):
        while True:
            self.fd = os.open(self.path, os.O_CREAT)
            fcntl.flock(self.fd, fcntl.LOCK_EX)

            # check if the file we hold the lock on is the same as the one
            # the path refers to. (another process might have recreated it)
            st0 = os.fstat(self.fd)
            try:
                st1 = os.stat(self.path)
                if st0.st_ino == st1.st_ino:
                    # both the same we locked the correct file
                    break
            except:
                # somethig went wrong. (e.g. some other process deleted the lock file?)
                # just try again
                pass
            # Try it again.
            os.close(self.fd)
            self.fd = None
        # We have a lock

    def release(self):
        # TODO: Do we have the lock?
        if self.fd is not None:
            os.unlink(self.path)
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
            self.fd = None

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, type, value, tb):
        self.release()


class FetchJob():
    """
    Fetch Job model to store details about fetch operation and its status
    """

    STATUS_PENDING = 'PENDING'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_FAILED = 'FAILED'
    STATUS_COMPLETE = 'COMPLETED'

    def __init__(self, jid):
        """
        Constructor
        @param id: Job identifier
        @type source: str
        """
        self.id = jid
        self.status = self.STATUS_PENDING
        self.start_timestamp = None
        self.end_timestamp = None
        self.reason = None

    def __eq__(self, other):
        if isinstance(other, FetchJob):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, FetchJob):
            return self.id != other.id
        return NotImplemented

    def update(self, **kwargs):
        if 'status' in kwargs:
            self.status = kwargs['status']
        if 'start_timestamp' in kwargs:
            self.start_timestamp = kwargs['start_timestamp']
        if 'end_timestamp' in kwargs:
            self.end_timestamp = kwargs['end_timestamp']
        if 'reason' in kwargs:
            self.reason = kwargs['reason']


def data_dir(request, data_url):
    """ Return an unique directory path for the data_url """
    # get fragment identifier and hash url without fragment
    url, fragment = urlparse.urldefrag(data_url)
    urlhash = hashlib.md5(url).hexdigest()
    dataroot = request.registry.settings['bccvl.mapscript.map_data_files_root_path']
    return os.path.join(dataroot, urlhash)


# FIXME: for large files we probably have to mave the file transfer to some other process...
#        something similar to the data mover interface.
#        e.g download, extract, optimise ....  when ready tell
#            UI OK ... otherwise tell progress and pending
def fetch_file(request, url):
    """Dowload the file from url and place it on the local file system.
    If file is a zip file it will be extracted to the local file system.

    The method returns the filename of the requested file on the
    local file system.
    """
    # TODO: optimize  data files for mapserver?
    # reproject/warp source? to avoid mapserver doing warp on the fly
    # otheroptions:
    #   convert to tiled raster (makes access to tiles faster)
    #     gdal_translate -co TILED=YES original.tif tiled.tif
    #   use Erdas Imagine (HFA) format ... always tiled and supports>4GB files
    #     gdal_translate -of HFA original.tif tiled.img
    #   add overview image to raster (after possible translate)
    #     gdaladdo [-r average] tiled.tif 2 4 8 16 32 64 128
    # for rs point data maybe convert to shapefile?
    if not (url.startswith('http://') or url.startswith('https://')):
        # TODO: probably allow more than just http and https
        #       and use better exception
        raise Exception('unsupported url scheme: %s', url)

    # Check if a local data file is already exist
    datadir = data_dir(request, url)
    url, fragment = urlparse.urldefrag(url)
    # FIXME: have to import here due to circular import
    from pyramid.settings import asbool
    with LockFile(datadir + '.lock'):
        if not os.path.exists(datadir):
            # the folder doesn't exist so we'll have to fetch the file
            # TODO: make sure there is no '..' in datadir
            os.makedirs(datadir)
            # not available yet so fetch it
            try:
                settings = request.registry.settings
                destfile = os.path.join(datadir, os.path.basename(url))
                try:
                    src = {
                        'url': url,
                        'verify': asbool(settings.get('bccvl.ssl.verify', True))
                    }
                    # do we have an __ac cookie?
                    cookie = request.cookies.get('__ac')
                    # get my tokens
                    tokens = ','.join([
                        token.strip()
                        for token in settings.get(
                            'authtkt.tokens', '').split('\n') if token.strip()
                    ])
                    if cookie:
                        src['cookies'] = {
                            'name': '__ac',
                            'value': update_auth_cookie(cookie, tokens, request),
                            'secure': True,
                            'domain': request.host,
                            'path': '/'
                        }
                    dst = {'url': 'file://{0}'.format(destfile)}
                    movelib.move(src, dst)
                except Exception as e:
                    # direct download failed what now?
                    LOG.exception('Failed to download data %s: %s', url, e)
                    raise
                # if it is a zip we should unpack it
                # FIXME: do some more robust zip detection
                if 'application/zip' in mimetypes.guess_type(destfile):
                    with zipfile.ZipFile(destfile, 'r') as zipf:
                        zipf.extractall(datadir)
                    # remove zipfile
                    os.remove(destfile)

                # search all tifs and try to generate overviews
                for root, dirnames, filenames in os.walk(datadir):
                    for filename in fnmatch.filter(filenames, '*.tif'):
                        rasterfile = os.path.join(root, filename)
                        ds = gdal.Open(rasterfile)
                        if ds:
                            maxlevel = min(ds.RasterXSize, ds.RasterYSize) / 512
                            ovrclear = ['gdaladdo', '-clean', rasterfile]
                            ovradd = ['gdaladdo', '-ro',
                                      #'--config', 'COMPRESS_OVERVIEW', 'LZW',
                                      rasterfile,
                            ]
                            level = 2
                            while level < maxlevel:
                                ovradd.append(str(level))
                                level = level * 2
                            if maxlevel >= 2:
                                subprocess.check_call(ovrclear)
                                subprocess.check_call(ovradd)

            except Exception as e:
                LOG.error('Could not download %s to %s : %s', url, datadir, e)
                shutil.rmtree(datadir)
                raise e
    # we have the data now construct the filepath
    filename = fragment if fragment else os.path.basename(url)
    # FIXME: make sure path.join works correctly (trailing/leading slash?)
    filename = os.path.join(datadir, filename)
    # make sure filename is within datadir
    filename = os.path.normpath(filename)
    if not os.path.normpath(filename).startswith(datadir):
        # FIXME: should probably check if filename exists and is supported
        #        and use better exception here
        raise Exception("Data file path not valid: '%s'", filename)
    return filename


from concurrent.futures import ThreadPoolExecutor
import datetime
import glob
import json
from bccvl_visualiser.models.external_api import DatabaseManager
from osgeo import ogr
import shlex
import subprocess

FETCH_EXECUTOR = ThreadPoolExecutor(max_workers=3)
FETCH_JOBS = {}


def fetch_worker(request, data_url, job):
    # get location of local data file
    job.update(
        status=FetchJob.STATUS_IN_PROGRESS,
        start_timestamp=datetime.datetime.now())

    try:
        loc = fetch_file(request, data_url)
        # FIXME: have to import here due to circular import
        from pyramid.settings import asbool
        install_to_db = asbool(request.params.get('INSTALL_TO_DB', False))

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
                dbFiles = [
                    dbfile
                    for dbfile in glob.glob(
                        os.path.join(datadir, fname, 'data/*.dbf'))
                ]
                if len(dbFiles) == 0:
                    dbFiles = [
                        dbfile
                        for dbfile in glob.glob(
                            os.path.join(datadir, fname, 'data/*.gdb.zip'))
                    ]
                if len(dbFiles) == 0:
                    raise Exception("Unsupported dataset type")

                # Import each df file into database
                metadata = {}
                for dbFilename in dbFiles:
                    dbfname = os.path.basename(dbFilename)

                    # Skip this db file if it has been imported before
                    # if DatabaseManager.get_metadata(filename) is not None:
                    #    continue

                    # Import db file into the database
                    schemaname = fname.replace('.', '_').replace('-',
                                                                 '_').lower()
                    import_into_db(dbFilename, schemaname)

                    # get the layer info as metadata.
                    md = get_dataset_metadata(schemaname, dbFilename)
                    metadata[dbfname] = md
                    # metadata.update(md)

                    # update the metadata stored in DatabaseManager
                    DatabaseManager.update_metadata(dbfname, md)

                # Save the metadata as json file for loading when visualiser
                # start
                jsonfile = open(os.path.join(datadir, "layer_info.json"), 'w')
                json.dump(metadata, jsonfile, indent=4)
                jsonfile.close()

        job.update(
            status=FetchJob.STATUS_COMPLETE,
            end_timestamp=datetime.datetime.now())
    except Exception as e:
        reason = 'Failed to fetch data from {0}. {1}'.format(data_url, str(e))
        LOG.warning(reason)
        job.update(
            status=FetchJob.STATUS_FAILED,
            end_timestamp=datetime.datetime.now(),
            reason=reason)


def get_dataset_metadata(schemaname, filepath):
    # list of table names for the given db file
    tablenames = get_tablenames(filepath)

    # Get info about the table
    metadata = {}
    for name in tablenames:
        tablename = schemaname + '.' + name.lower()
        extent, fieldnames = get_layerinfo_from_db(tablename)

        md = {'table': tablename, 'fields': fieldnames, 'id_column': 'fid'}

        # dataset only has extent if it has geometry column.
        if extent:
            xmin, xmax, ymin, ymax = extent
            md['base_extent'] = {
                'xmin': xmin,
                'ymin': ymin,
                'xmax': xmax,
                'ymax': ymax
            }
            md['geometry_column'] = 'geom'
        metadata[name.lower()] = md
    return metadata


def get_layerinfo_from_db(tablename):
    # Get extent of the table specified from DB server
    command = 'PG:{dbconn}'.format(dbconn=DatabaseManager.connection_details())
    dbconn = ogr.Open(command)
    # layerdata = dbconn.ExecuteSQL("select * from
    # {table}".format(table=tablename))
    layerdata = dbconn.GetLayer(str(tablename))

    # Get a list of user defined column names
    layerdefn = layerdata.GetLayerDefn()
    fieldnames = [
        layerdefn.GetFieldDefn(i).GetName()
        for i in range(layerdefn.GetFieldCount())
    ]

    extent = None
    if len(layerdata.GetGeometryColumn()) > 0:
        extent = layerdata.GetExtent()
    dbconn.Destroy()
    return extent, fieldnames


def import_into_db(dbfname, schemaname):
    # Import dataset into db server
    try:
        # create schema
        command = 'ogrinfo -so PG:"{dbconn}" -sql "create schema if not exists {schema}"'.format(
            dbconn=DatabaseManager.connection_details(), schema=schemaname)
        p = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        output, err = p.communicate()
        if p.returncode != 0 or len(err) > 0:
            raise Exception("Fail to create schema '{}'. {}".format(schemaname,
                                                                    err))

        # import the dataset. Set FID and geometry name.
        command = 'ogr2ogr -f PostgreSQL PG:"{dbconn}" -lco schema={schema} -lco FID=fid -lco GEOMETRY_NAME=geom  {dbfile} -skipfailures -overwrite --config PG_USE_COPY YES'.format(
            dbconn=DatabaseManager.connection_details(),
            schema=schemaname,
            dbfile=dbfname)
        p = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        output, err = p.communicate()
        if p.returncode != 0 or len(err) > 0:
            raise Exception("Fail to import dataset '{}. {}'".format(dbfname,
                                                                     err))

    except Exception as e:
        raise Exception("Failed to import dataset into DB server. {0}".format(
            str(e)))


def get_tablenames(dbfname):
    command = "ogrinfo -so -q {filename}".format(filename=dbfname)
    p = subprocess.Popen(
        shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    if p.returncode != 0 or len(err) > 0:
        raise Exception("Fail to get table names from '{}': {}".format(dbfname,
                                                                       err))

    # parse for tablenames.
    # output format: 1: tablename1 (None) \n\r2: tablename2 (polygon) \n\r3:
    tokens = output.split(":")
    names = [tokens[i].split()[0].strip() for i in range(1, len(tokens))]
    return names
