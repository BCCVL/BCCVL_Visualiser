import unittest
import mock
import datetime
from time import sleep

from pyramid.request import Request

from bccvl_visualiser.views.api import ApiCollectionView
from bccvl_visualiser.utils import FetchJob


class TestApiCollectionView(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_api_collection_view_submit_new_job(self):
        request = Request({})
        view = None
        with mock.patch('bccvl_visualiser.views.get_localizer', side_effect=[None]) as mock_get_localizer:
            with mock.patch('pyramid.request.Request.GET', side_effect=[None]) as mock_request_get:
                with mock.patch('bccvl_visualiser.utils.fetch_file', side_effect=['/tmp/abc/filename']):
                    with mock.patch('bccvl_visualiser.utils.data_dir', side_effect=['/tmp/def', '/tmp/def']):
                        with mock.patch('bccvl_visualiser.utils.fetch_worker'):
                            view = ApiCollectionView({}, request)
                            resp = view.fetch()

                            job = view._fetch_jobs['/tmp/def']
                            self.assertEqual(view.request, request)
                            self.assertEqual(job.status, FetchJob.STATUS_PENDING)
                            self.assertEqual(resp, {'status': FetchJob.STATUS_PENDING, 'reason': None})

    def test_api_collection_view_not_submit_job(self):
        request = Request({})
        view = None
        with mock.patch('bccvl_visualiser.views.get_localizer', side_effect=[None]) as mock_get_localizer:
            with mock.patch('pyramid.request.Request.GET', side_effect=[None]) as mock_request_get:
                with mock.patch('bccvl_visualiser.utils.fetch_file', side_effect=['/tmp/abc/filename']):
                    with mock.patch('bccvl_visualiser.utils.data_dir', side_effect=['/tmp/def', '/tmp/def']):
                        with mock.patch('bccvl_visualiser.utils.fetch_worker'):
                            view = ApiCollectionView({}, request)
                            resp = view.fetch()

                            # Check that second fetch does not submit another job
                            resp = view.fetch()
                            self.assertEqual(view._fetch_jobs.keys(), ['/tmp/def'])
                            self.assertEqual(resp, {'status': FetchJob.STATUS_PENDING, 'reason': None})

                            job = view._fetch_jobs['/tmp/def']
                            self.assertEqual(view.request, request)
                            self.assertEqual(job.status, FetchJob.STATUS_PENDING)
                            self.assertEqual(resp, {'status': FetchJob.STATUS_PENDING, 'reason': None})

    def test_api_collection_view_remove_completed_job(self):
        request = Request({})
        view = None
        with mock.patch('bccvl_visualiser.views.get_localizer', side_effect=[None]) as mock_get_localizer:
            with mock.patch('pyramid.request.Request.GET', side_effect=[None]) as mock_request_get:
                with mock.patch('bccvl_visualiser.views.api.fetch_file', side_effect=['/tmp/abc/filename']):
                    with mock.patch('bccvl_visualiser.views.api.data_dir', side_effect=['/tmp/def', '/tmp/def']):
                        with mock.patch('bccvl_visualiser.views.api.fetch_worker'):
                            view = ApiCollectionView({}, request)
                            resp = view.fetch()

                            job = view._fetch_jobs['/tmp/def']
                            self.assertEqual(view.request, request)
                            self.assertEqual(job.status, FetchJob.STATUS_PENDING)
                            self.assertEqual(resp, {'status': FetchJob.STATUS_PENDING, 'reason': None})

                            job.update(status=FetchJob.STATUS_COMPLETE, start_timestamp=datetime.datetime.now())
                            self.assertEqual(job.status, FetchJob.STATUS_COMPLETE)

                            resp = view.fetch()
                            self.assertEqual(job.status, FetchJob.STATUS_COMPLETE)
                            self.assertEqual(view._fetch_jobs.keys(), [])
                            self.assertEqual(resp, {'status': FetchJob.STATUS_COMPLETE, 'reason': None})

    def test_api_collection_view_remove_failed_job(self):
        request = Request({})
        view = None
        with mock.patch('bccvl_visualiser.views.get_localizer', side_effect=[None]) as mock_get_localizer:
            with mock.patch('pyramid.request.Request.GET', side_effect=[None]) as mock_request_get:
                with mock.patch('bccvl_visualiser.utils.fetch_file', side_effect=['/tmp/abc/filename']):
                    with mock.patch('bccvl_visualiser.utils.data_dir', side_effect=['/tmp/def', '/tmp/def']):
                        with mock.patch('bccvl_visualiser.utils.fetch_worker'):
                            view = ApiCollectionView({}, request)
                            resp = view.fetch()

                            job = view._fetch_jobs['/tmp/def']
                            self.assertEqual(view.request, request)
                            self.assertEqual(job.status, FetchJob.STATUS_PENDING)
                            self.assertEqual(resp, {'status': FetchJob.STATUS_PENDING, 'reason': None})

                            reason = "job failed!"
                            job.update(status=FetchJob.STATUS_FAILED, start_timestamp=datetime.datetime.now(), reason=reason)
                            self.assertEqual(job.status, FetchJob.STATUS_FAILED)

                            resp = view.fetch()
                            self.assertEqual(job.status, FetchJob.STATUS_FAILED)
                            self.assertEqual(view._fetch_jobs.keys(), [])
                            self.assertEqual(resp, {'status': FetchJob.STATUS_FAILED, 'reason': reason})

    def test_api_collection_view_data_exists(self):
        request = Request({})
        view = None
        with mock.patch('bccvl_visualiser.views.get_localizer', side_effect=[None]) as mock_get_localizer:
            with mock.patch('pyramid.request.Request.GET', side_effect=[None]) as mock_request_get:
                with mock.patch('bccvl_visualiser.utils.fetch_file', side_effect=['/tmp/abc/filename']):
                    with mock.patch('bccvl_visualiser.utils.data_dir', side_effect=['/tmp/def', '/tmp/def']):
                        with mock.patch('os.path.exists', side_effect=[True]):
                            view = ApiCollectionView({}, request)
                            resp = view.fetch()

                            self.assertEqual(view._fetch_jobs.keys(), [])
                            self.assertEqual(resp, {'status': FetchJob.STATUS_COMPLETE, 'reason': None})

    def test_api_collection_view_download_data_exception(self):
        request = Request({})
        view = None
        with mock.patch('bccvl_visualiser.views.get_localizer', side_effect=[None]) as mock_get_localizer:
            with mock.patch('pyramid.request.Request.GET', side_effect=[None]) as mock_request_get:
                with mock.patch('bccvl_visualiser.utils.fetch_file', side_effect=Exception("Bad file")):
                    with mock.patch('bccvl_visualiser.utils.data_dir', side_effect=['/tmp/def', '/tmp/def']):
                        view = ApiCollectionView({}, request)
                        resp = view.fetch()

                        sleep(0.2)
                        job = view._fetch_jobs['/tmp/def']
                        resp = view.fetch()
                        self.assertEqual(job.status, FetchJob.STATUS_FAILED)
                        self.assertTrue(resp['reason'].find('Bad file') != -1)
