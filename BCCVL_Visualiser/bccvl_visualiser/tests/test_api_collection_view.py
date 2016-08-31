import unittest
import mock
import datetime
from time import sleep

from pyramid.request import Request

from bccvl_visualiser.views.api import ApiCollectionView
from bccvl_visualiser.utils import FetchJob, FETCH_JOBS


@mock.patch('bccvl_visualiser.views.api.data_dir', return_value='/tmp/def')
@mock.patch('pyramid.request.Request.GET', return_value=None)
@mock.patch('bccvl_visualiser.views.get_localizer', return_value=None)
class TestApiCollectionView(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('bccvl_visualiser.views.api.fetch_worker')
    @mock.patch('bccvl_visualiser.utils.fetch_file',
                return_value='/tmp/abc/filename')
    def test_api_collection_view_submit_new_job(self, *mocks):
        request = Request({})
        view = ApiCollectionView({}, request)
        resp = view.fetch()

        job = FETCH_JOBS['/tmp/def']
        self.assertEqual(view.request, request)
        self.assertEqual(job.status, FetchJob.STATUS_PENDING)
        self.assertEqual(resp, {'status': FetchJob.STATUS_PENDING,
                                'reason': None})

    @mock.patch('bccvl_visualiser.views.api.fetch_worker')
    @mock.patch('bccvl_visualiser.utils.fetch_file',
                return_value='/tmp/abc/filename')
    def test_api_collection_view_not_submit_job(self, *mocks):
        request = Request({})
        view = ApiCollectionView({}, request)
        resp = view.fetch()

        # Check that second fetch does not submit another job
        resp = view.fetch()
        self.assertEqual(FETCH_JOBS.keys(), ['/tmp/def'])
        self.assertEqual(resp, {'status': FetchJob.STATUS_PENDING,
                                'reason': None})

        job = FETCH_JOBS['/tmp/def']
        self.assertEqual(view.request, request)
        self.assertEqual(job.status, FetchJob.STATUS_PENDING)
        self.assertEqual(resp, {'status': FetchJob.STATUS_PENDING,
                                'reason': None})

    @mock.patch('bccvl_visualiser.views.api.fetch_worker')
    @mock.patch('bccvl_visualiser.utils.fetch_file',
                return_value='/tmp/abc/filename')
    def test_api_collection_view_remove_completed_job(self, *mocks):
        request = Request({})
        view = ApiCollectionView({}, request)
        resp = view.fetch()

        job = FETCH_JOBS['/tmp/def']
        self.assertEqual(view.request, request)
        self.assertEqual(job.status, FetchJob.STATUS_PENDING)
        self.assertEqual(resp, {'status': FetchJob.STATUS_PENDING,
                                'reason': None})

        job.update(status=FetchJob.STATUS_COMPLETE,
                   start_timestamp=datetime.datetime.now())
        self.assertEqual(job.status, FetchJob.STATUS_COMPLETE)

        resp = view.fetch()
        self.assertEqual(job.status, FetchJob.STATUS_COMPLETE)
        self.assertEqual(FETCH_JOBS.keys(), [])
        self.assertEqual(resp, {'status': FetchJob.STATUS_COMPLETE,
                                'reason': None})

    @mock.patch('bccvl_visualiser.views.api.fetch_worker')
    @mock.patch('bccvl_visualiser.utils.fetch_file',
                return_value='/tmp/abc/filename')
    def test_api_collection_view_remove_failed_job(self, *mocks):
        request = Request({})
        view = ApiCollectionView({}, request)
        resp = view.fetch()

        job = FETCH_JOBS['/tmp/def']
        self.assertEqual(view.request, request)
        self.assertEqual(job.status, FetchJob.STATUS_PENDING)
        self.assertEqual(resp, {'status': FetchJob.STATUS_PENDING,
                                'reason': None})

        reason = "job failed!"
        job.update(status=FetchJob.STATUS_FAILED,
                   start_timestamp=datetime.datetime.now(),
                   reason=reason)
        self.assertEqual(job.status, FetchJob.STATUS_FAILED)

        resp = view.fetch()
        self.assertEqual(job.status, FetchJob.STATUS_FAILED)
        self.assertEqual(FETCH_JOBS.keys(), [])
        self.assertEqual(resp, {'status': FetchJob.STATUS_FAILED,
                                'reason': reason})

    @mock.patch('bccvl_visualiser.views.api.fetch_worker')
    @mock.patch('bccvl_visualiser.utils.fetch_file',
                return_value='/tmp/abc/filename')
    @mock.patch('os.path.exists', return_value=True)
    def test_api_collection_view_data_exists(self, *mocks):
        request = Request({})
        view = ApiCollectionView({}, request)
        resp = view.fetch()

        self.assertEqual(FETCH_JOBS.keys(), [])
        self.assertEqual(resp, {'status': FetchJob.STATUS_COMPLETE,
                                'reason': None})

    @mock.patch('bccvl_visualiser.utils.fetch_file',
                side_effect=Exception("Bad file"))
    def test_api_collection_view_download_data_exception(self, *mocks):
        request = Request({})
        view = ApiCollectionView({}, request)
        resp = view.fetch()

        sleep(0.2)
        job = FETCH_JOBS['/tmp/def']
        resp = view.fetch()
        self.assertEqual(job.status, FetchJob.STATUS_FAILED)
        self.assertTrue(resp['reason'].find('Bad file') != -1)
