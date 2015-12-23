import logging
import os
import datetime

from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from sqlalchemy.exc import DBAPIError

from bccvl_visualiser.models import (
    APICollection
    )

from bccvl_visualiser.views import BaseView
from bccvl_visualiser.utils import FetchJob, fetch_file, data_dir
from concurrent.futures import ThreadPoolExecutor

LOG = logging.getLogger(__name__)

def fetch_worker(request, data_url, job):
    # get location of local data file
    job.update(status=FetchJob.STATUS_IN_PROGRESS, start_timestamp=datetime.datetime.now())
    try:
        loc = fetch_file(request, data_url)
        job.update(status=FetchJob.STATUS_COMPLETE, end_timestamp=datetime.datetime.now())
    except Exception as e:
        reason = 'Failed to fetch data from {0}. {1}'.format(data_url, str(e))
        LOG.warning(reason)
        job.update(status=FetchJob.STATUS_FAILED, end_timestamp=datetime.datetime.now(), reason=reason)


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
