import unittest
import transaction
import pprint
import json

from pyramid import testing

from bccvl_visualiser.models import *
from paste.deploy.loadwsgi import appconfig

pp = pprint.PrettyPrinter(indent=4)

class TestHTMLAPIv1(unittest.TestCase):
    def setUp(self):
        self.config = appconfig('config:development.ini', 'pyramid', relative_to='.')
        from bccvl_visualiser import main
        app = main(None, **self.config)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        pass

    def test_view_html_api_html(self):
       res = self.testapp.get('/api/html', status='*')
       self.assertEqual(res.status_int, 200)

    def test_view_html_api_v1_html(self):
       res = self.testapp.get('/api/html/1', status='*')
       self.assertEqual(res.status_int, 200)

    def test_test_env_working(self):
        self.assertEqual(True, True)

    def test_html_in_api_collection(self):
        self.assertTrue(BaseHTMLAPI in APICollection.base_api_inheritors())

    def test_html_in_api_collection_to_dict(self):
        api_dict = APICollection.to_dict()
        self.assertEqual(api_dict['html']['name'], 'html')

    def test_html_direct_inheritors_version_dict(self):
        """This test will fail if a new version of the HTML API is added"""
        inheritors_version_dict = BaseHTMLAPI.get_direct_inheritors_version_dict()

        self.assertEqual(inheritors_version_dict[1], HTMLAPIv1)
        self.assertEqual(len(inheritors_version_dict), 1)

    def test_html_api_identifier(self):
        self.assertEqual(BaseHTMLAPI.identifier(), 'html')

    def test_version(self):
        self.assertEqual(HTMLAPIv1.version(), 1, msg="Version should be 1")

    def test_to_dict(self):
        name = HTMLAPIv1.identifier()
        description = HTMLAPIv1.description()
        version = HTMLAPIv1.version()

        the_dict = HTMLAPIv1.to_dict()

        self.assertEqual(the_dict['name'], name, msg="Name should match")
        self.assertEqual(the_dict['description'], description, msg="Description should match")
        self.assertEqual(the_dict['version'], version, msg="Version should match")

    def test_view_html_api_v1_html(self):
        params = {
            'data_url':     'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/hello_world.html',
        }

        res = self.testapp.get('/api/html/1/data_url_view', status='*', params=params)
        self.assertEqual(res.status_int, 200)

        self.assertEqual(res.content_type, 'text/html')

    def test_url_replacement(self):
        url = "http://compute.bccvl.org.au/experiments/bioclim-unthemed/bioclim-unthemed-result-2013-11-20t00-47-41-120241/results.html/view/++widget++form.widgets.file/@@download/results.html"

        html_string = '''<html><img src="AUC.png" /><img src='ALL.png' /></html>'''
        expected_content = '''<html><img src="http://compute.bccvl.org.au/experiments/bioclim-unthemed/bioclim-unthemed-result-2013-11-20t00-47-41-120241/AUC.png/view/++widget++form.widgets.file/@@download/AUC.png" /><img src="http://compute.bccvl.org.au/experiments/bioclim-unthemed/bioclim-unthemed-result-2013-11-20t00-47-41-120241/ALL.png/view/++widget++form.widgets.file/@@download/ALL.png" /></html>'''

        out_content = HTMLAPIv1.replace_urls(html_string, url)

        self.assertEqual(out_content, expected_content)
