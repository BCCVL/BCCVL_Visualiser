import unittest
import transaction

from pyramid import testing

from bccvl_visualiser.models import BasePNGAPI, PNGAPIv1, APICollection, FDataMover
from paste.deploy.loadwsgi import appconfig

class TestPNGAPIv1(unittest.TestCase):
    def setUp(self):
        FDataMover.local = True

        self.config = appconfig('config:development.ini', 'pyramid', relative_to='.')
        from bccvl_visualiser import main
        app = main(None, **self.config)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        FDataMover.local = False

    def test_view_png_api_r(self):
       res = self.testapp.get('/api/png', status='*')
       self.assertEqual(res.status_int, 200)

    def test_view_png_api_v1_r(self):
       res = self.testapp.get('/api/png/1', status='*')
       self.assertEqual(res.status_int, 200)

    def test_test_env_working(self):
        self.assertEqual(True, True)

    def test_png_in_api_collection(self):
        self.assertTrue(BasePNGAPI in APICollection.base_api_inheritors())

    def test_png_in_api_collection_to_dict(self):
        api_dict = APICollection.to_dict()
        self.assertEqual(api_dict['png']['name'], 'png')

    def test_png_direct_inheritors_version_dict(self):
        """This test will fail if a new version of the PNG API is added"""
        inheritors_version_dict = BasePNGAPI.get_direct_inheritors_version_dict()

        self.assertEqual(inheritors_version_dict[1], PNGAPIv1)
        self.assertEqual(len(inheritors_version_dict), 1)

    def test_png_api_identifier(self):
        self.assertEqual(BasePNGAPI.identifier(), 'png')

    def test_version(self):
        self.assertEqual(PNGAPIv1.version(), 1, msg="Version should be 1")

    def test_to_dict(self):
        name = PNGAPIv1.identifier()
        description = PNGAPIv1.description()
        version = PNGAPIv1.version()

        the_dict = PNGAPIv1.to_dict()

        self.assertEqual(the_dict['name'], name, msg="Name should match")
        self.assertEqual(the_dict['description'], description, msg="Description should match")
        self.assertEqual(the_dict['version'], version, msg="Version should match")

    def test_view_png_api_v1_data_url_view(self):
        params = {
            'data_url':     'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/smile.png',
        }

        res = self.testapp.get('/api/png/1/data_url_view', status='*', params=params)

        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.content_type, 'image/png')
