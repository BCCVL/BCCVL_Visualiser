import unittest
import transaction
import pprint
import json

from pyramid import testing

from bccvl_visualiser.models import BaseCSVAPI, CSVAPIv1, APICollection, FDataMover

from paste.deploy.loadwsgi import appconfig

class TestCSVAPIv1(unittest.TestCase):

    def setUp(self):
        FDataMover.LOCAL = True

        self.config = appconfig('config:development.ini', 'pyramid', relative_to='.')
        from bccvl_visualiser import main
        app = main(None, **self.config)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        FDataMover.LOCAL = False

    def test_view_csv_api_html(self):
       res = self.testapp.get('/api/csv', status='*')
       self.assertEqual(res.status_int, 200)

    def test_view_csv_api_v1_html(self):
       res = self.testapp.get('/api/csv/1', status='*')
       self.assertEqual(res.status_int, 200)

    def test_csv_in_api_collection(self):
        self.assertTrue(BaseCSVAPI in APICollection.base_api_inheritors())

    def test_csv_in_api_collection_to_dict(self):
        api_dict = APICollection.to_dict()
        self.assertEqual(api_dict['csv']['name'], 'csv')

    def test_csv_direct_inheritors_version_dict(self):
        """This test will fail if a new version of the CSV API is added"""
        inheritors_version_dict = BaseCSVAPI.get_direct_inheritors_version_dict()

        self.assertEqual(inheritors_version_dict[1], CSVAPIv1)
        self.assertEqual(len(inheritors_version_dict), 1)

    def test_csv_api_identifier(self):
        self.assertEqual(BaseCSVAPI.identifier(), 'csv')

    def test_version(self):
        self.assertEqual(CSVAPIv1.version(), 1, msg="Version should be 1")

    def test_to_dict(self):
        name = CSVAPIv1.identifier()
        description = CSVAPIv1.description()
        version = CSVAPIv1.version()

        the_dict = CSVAPIv1.to_dict()

        self.assertEqual(the_dict['name'], name, msg="Name should match")
        self.assertEqual(the_dict['description'], description, msg="Description should match")
        self.assertEqual(the_dict['version'], version, msg="Version should match")

    def test_create_and_render_csv_as_html_tabl_via_point_api_v1(self):
        params = {
            'data_url':     'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv',
        }

        res = self.testapp.get('/api/csv/1/data_url_view', status='*', params=params)

        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.content_type, 'text/html')
        expected_output = """
<!DOCTYPE html>
<html style="width:100%; height:100%">

    <head>
        <title>CSV V1 View</title>
        <link href="http://localhost/static/bccvl.css" rel="stylesheet" type="text/css">
    </head>

    <body>
<table><thead><tr><th>species</th><th>lon</th><th>lat</th></tr></thead><tbody><tr><td>Dromaius novaehollandiae</td><td>32.09</td><td>42.12</td></tr><tr><td>Dromaius novaehollandiae</td><td>45</td><td>21</td></tr><tr><td>Dromaius novaehollandiae</td><td>56.43</td><td>43.22</td></tr><tr><td>Dromaius novaehollandiae</td><td>179</td><td>-89.01</td></tr></tbody></table>
    </body>
</html>
"""
        self.assertEqual(res.body.strip(), expected_output.strip())
