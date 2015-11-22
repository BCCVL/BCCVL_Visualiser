import hashlib
import os
import os.path
import fcntl
import zipfile
import urlparse
import shutil
import logging
from pyrmaid.settings import asbool
from org.bccvl import movelib


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

    # get fragment identifier and hash url without fragment
    if not (url.startswith('http://') or url.startswith('https://')):
        # TODO: probably allow more than just http and https
        #       and use better exception
        raise Exception('unsupported url scheme: %s', url)
    url, fragment = urlparse.urldefrag(url)
    # TODO: would be nice to use datasetid here
    urlhash = hashlib.md5(url).hexdigest()
    # check if we have the file already
    dataroot = request.registry.settings['bccvl.mapscript.map_data_files_root_path']
    datadir = os.path.join(dataroot, urlhash)

    with LockFile(datadir + '.lock'):
        if not os.path.exists(datadir):
            # the folder doesn't exist so we'll have to fetch the file
            # TODO: make sure there is no '..' in datadir
            os.makedirs(datadir)
            # not available yet so fetch it
            try:
                destfile = os.path.join(datadir, os.path.basename(url))
                try:
                    src = {
                        'url': url,
                        'verify': asbool(request.registry.settings.get('bccvl.ssl.verify', True))
                    }
                    # do we have an __ac cookie?
                    cookie = request.cookies.get('__ac')
                    if cookie:
                        src['cookies'] = {
                            'name': '__ac',
                            'value': cookie,
                            'secure': True,
                            'domain': request.host,
                            'path': '/'
                        }
                    dst = {
                        'url': 'file://{0}'.format(destfile)
                    }
                    movelib.move(src, dst)
                except Exception as e:
                    # direct download failed what now?
                    LOG.exception('Failed to download data %s: %s', url, e)
                    raise
                # if it is a zip we should unpack it
                # FIXME: do some more robust zip detection
                if fragment:
                    with zipfile.ZipFile(destfile, 'r') as zipf:
                        zipf.extractall(datadir)
                    # remove zipfile
                    os.remove(destfile)
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
