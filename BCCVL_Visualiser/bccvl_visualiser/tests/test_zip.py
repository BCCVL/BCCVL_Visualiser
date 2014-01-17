import unittest
import transaction

from pyramid import testing

from bccvl_visualiser.models import BaseZIPAPI, ZIPAPIv1, APICollection
from paste.deploy.loadwsgi import appconfig

class TestZIPAPIv1(unittest.TestCase):
    def setUp(self):
        self.config = appconfig('config:development.ini', 'pyramid', relative_to='.')
        from bccvl_visualiser import main
        app = main(None, **self.config)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        pass

    def test_view_zip_api_r(self):
       res = self.testapp.get('/api/zip', status='*')
       self.assertEqual(res.status_int, 200)

    def test_view_zip_api_v1_r(self):
       res = self.testapp.get('/api/zip/1', status='*')
       self.assertEqual(res.status_int, 200)

    def test_test_env_working(self):
        self.assertEqual(True, True)

    def test_zip_in_api_collection(self):
        self.assertTrue(BaseZIPAPI in APICollection.base_api_inheritors())

    def test_zip_in_api_collection_to_dict(self):
        api_dict = APICollection.to_dict()
        self.assertEqual(api_dict['zip']['name'], 'zip')

    def test_zip_direct_inheritors_version_dict(self):
        """This test will fail if a new version of the ZIP API is added"""
        inheritors_version_dict = BaseZIPAPI.get_direct_inheritors_version_dict()

        self.assertEqual(inheritors_version_dict[1], ZIPAPIv1)
        self.assertEqual(len(inheritors_version_dict), 1)

    def test_zip_api_identifier(self):
        self.assertEqual(BaseZIPAPI.identifier(), 'zip')

    def test_version(self):
        self.assertEqual(ZIPAPIv1.version(), 1, msg="Version should be 1")

    def test_to_dict(self):
        name = ZIPAPIv1.identifier()
        description = ZIPAPIv1.description()
        version = ZIPAPIv1.version()

        the_dict = ZIPAPIv1.to_dict()

        self.assertEqual(the_dict['name'], name, msg="Name should match")
        self.assertEqual(the_dict['description'], description, msg="Description should match")
        self.assertEqual(the_dict['version'], version, msg="Version should match")

    def test_view_zip_api_v1_data_url_view(self):
        params = {
            'data_url':     'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/env_layers.zip',
            'file_name':    'bioclim_15.tif'
        }

        res = self.testapp.get('/api/zip/1/data_url_view', status='*', params=params)

        self.assertEqual(res.status_int, 302)
