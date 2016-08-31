import logging
import os

from pyramid.view import view_config, view_defaults

from bccvl_visualiser.models import (
    APICollection
)

from bccvl_visualiser.views import BaseView
from bccvl_visualiser.utils import (
    FetchJob, data_dir, FETCH_JOBS, FETCH_EXECUTOR, fetch_worker
)

LOG = logging.getLogger(__name__)


@view_defaults(route_name='api')
class ApiCollectionView(BaseView):
    """The API level view"""

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
            return self.StatusResponse(FetchJob.STATUS_FAILED,
                                       'No data_url provided')

        # Check if a job has been submitted or data has been dowbloaded for
        # this data url.
        datadir = data_dir(self.request, data_url)
        job = FETCH_JOBS.get(datadir)
        if job:
            # existing job,... return status
            reason = job.reason
            status = job.status
            # TODO: if job is completed it can be removed right away
            #       elif clause below should catch that case anyway
            if job.status in (FetchJob.STATUS_FAILED,
                              FetchJob.STATUS_COMPLETE):
                # job in end state ... delete it and report state back
                del FETCH_JOBS[datadir]
            return self.StatusResponse(status, reason)
        elif os.path.exists(datadir):
            # no job ... and path exists
            return self.StatusResponse(FetchJob.STATUS_COMPLETE)

        # Submit a new fetch job with datadir as job ID.
        job = FetchJob(datadir)
        FETCH_JOBS[datadir] = job
        # TODO: should we really hang on to request object for a potentially long time?
        FETCH_EXECUTOR.submit(fn=fetch_worker, request=self.request,
                              data_url=data_url, job=job)
        return self.StatusResponse(job.status, job.reason)

    def _to_dict(self):
        return APICollection.to_dict()

    def StatusResponse(self, status, reason=None):
        return {'status': status, 'reason': reason}
