import bccvl_visualiser
import unittest
import transaction
import pprint
import json
import mapscript
import time

from pyramid import testing

from bccvl_visualiser.models import PointAPIv1, APICollection, BasePointAPI, FDataMover
from paste.deploy.loadwsgi import appconfig

pp = pprint.PrettyPrinter(indent=4)

class TestPointAPIv1(unittest.TestCase):
    def setUp(self):
        FDataMover.local = True

        self.config = appconfig('config:development.ini', 'pyramid', relative_to='.')
        from bccvl_visualiser import main
        app = main(None, **self.config)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        FDataMover.local = False

    def test_view_point_api_html(self):
       res = self.testapp.get('/api/point', status='*')
       self.assertEqual(res.status_int, 200)

    def test_view_point_api_v1_html(self):
       res = self.testapp.get('/api/point/1', status='*')
       self.assertEqual(res.status_int, 200)

    def test_test_env_working(self):
        self.assertEqual(True, True)

    def test_point_in_api_collection(self):
        self.assertTrue(BasePointAPI in APICollection.base_api_inheritors())

    def test_point_in_api_collection_to_dict(self):
        api_dict = APICollection.to_dict()
        self.assertEqual(api_dict['point']['name'], 'point')

    def test_point_direct_inheritors_version_dict(self):
        """This test will fail if a new version of the Point API is added"""
        inheritors_version_dict = BasePointAPI.get_direct_inheritors_version_dict()

        self.assertEqual(inheritors_version_dict[1], PointAPIv1)
        self.assertEqual(len(inheritors_version_dict), 1)

    def test_point_api_identifier(self):
        self.assertEqual(BasePointAPI.identifier(), 'point')

    def test_version(self):
        self.assertEqual(PointAPIv1.version(), 1, msg="Version should be 1")

    def test_to_dict(self):
        name = PointAPIv1.identifier()
        description = PointAPIv1.description()
        version = PointAPIv1.version()

        the_dict = PointAPIv1.to_dict()

        self.assertEqual(the_dict['name'], name, msg="Name should match")
        self.assertEqual(the_dict['description'], description, msg="Description should match")
        self.assertEqual(the_dict['version'], version, msg="Version should match")

    def test_create_and_render_wms_map_via_point_api_v1(self):
        data_url     = "https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv"
        query_string = "TRANSPARENT=true&FORMAT=image%2Fpng&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&STYLES=&SRS=EPSG%3A3857&BBOX=-20037508.34,-10018754.17,-15028131.255,-5009377.085&WIDTH=512&HEIGHT=1024&LAYERS=DEFAULT"
        my_map = PointAPIv1(data_url=data_url, query_string=query_string)
        map_content, map_content_type, retval = my_map.render()

        self.assertEqual(map_content_type, "image/png")
        self.assertEqual(retval, mapscript.MS_SUCCESS, "Should return success code: %s, but didn't" % mapscript.MS_SUCCESS)

    def test_create_and_render_wfs_map_via_point_api_v1(self):
        data_url     = "https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv"
        query_string = "request=GetFeature&service=WFS&version=1.1.0&typeName=DEFAULT&outputFormat=geojson"
        my_map = PointAPIv1(data_url=data_url, query_string=query_string)
        map_content, map_content_type, retval = my_map.render()

        self.assertEqual(map_content_type, "application/json; subtype=geojson")
        self.assertEqual(retval, mapscript.MS_SUCCESS, "Should return success code: %s, but didn't" % mapscript.MS_SUCCESS)

    # TODO - Check if this is fixed in newer versions of mapscript.
    @unittest.skip("WFS GeoJSON response is missing the point with the largest lat and lng value. This is a bug in mapscript")
    def test_create_and_render_wfs_map_via_point_api_v1__check_content(self):
        data_url     = "https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv"
        query_string = "request=GetFeature&service=WFS&version=1.1.0&typeName=DEFAULT&outputFormat=geojson"
        my_map = PointAPIv1(data_url=data_url, query_string=query_string)
        map_content, map_content_type, retval = my_map.render()
        expected_content= '''features": [\n    \n    {\n      "type": "Feature",\n      "geometry": {\n        "type": "Point",\n        "coordinates": [32.09, 42.12]\n      },\n      "properties": {\n      }\n    },\n    \n    {\n      "type": "Feature",\n      "geometry": {\n        "type": "Point",\n        "coordinates": [45, 21]\n      },\n      "properties": {\n      }\n    },\n    \n    {\n      "type": "Feature",\n      "geometry": {\n        "type": "Point",\n        "coordinates": [56.43, 43.22]\n      },\n      "properties": {\n      }\n    },\n    \n    {\n      "type": "Feature",\n      "geometry": {\n        "type": "Point",\n        "coordinates": [179, -89.01]\n      },\n      "properties": {\n      }\n    }\n  ]\n}\n\n'''

        self.assertEqual(map_content, expected_content)
        self.assertEqual(map_content_type, "application/json; subtype=geojson")
        self.assertEqual(retval, mapscript.MS_SUCCESS, "Should return success code: %s, but didn't" % mapscript.MS_SUCCESS)

    def test_view_point_api_v1_json(self):
        res = self.testapp.get('/api/point/1.json', status='*')
        self.assertEqual(res.status_int, 200)

        loaded_json = json.loads(res.body)
        self.assertEqual(loaded_json['version'], PointAPIv1.version())
        self.assertEqual(loaded_json['name'], PointAPIv1.identifier())

    def test_view_point_api_wfs(self):
        params = {
            'DATA_URL':     'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv',
            'request':      'GetFeature',
            'service':      'WFS',
            'version':      '1.1.0',
            'typeName':     'DEFAULT',
            'outputFormat': 'geojson',
        }
        res = self.testapp.get('/api/point/1/wfs_data_url', status='*', params=params)
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.content_type, 'application/json')

        loaded_json = json.loads(res.body)
        self.assertEqual(type(loaded_json), dict)
        self.assertEqual(loaded_json['type'], 'FeatureCollection')

    @unittest.skip("WFS GeoJSON response is missing the point with the largest lat and lng value. This is a bug in mapscript")
    def test_view_point_api_wfs_content(self):
        params = {
            'DATA_URL':     'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv',
            'request':      'GetFeature',
            'service':      'WFS',
            'version':      '1.1.0',
            'typeName':     'DEFAULT',
            'outputFormat': 'geojson',
        }
        res = self.testapp.get('/api/point/1/wfs_data_url', status='*', params=params)
        self.assertEqual(res.status_int, 200)

        loaded_json = json.loads(res.body)
        self.assertEqual(type(loaded_json), dict)

        self.assertEqual(len(loaded_json['features']), 4)

    # Spherical Mercator
    def test_view_point_api_wms_srs_epsg_3857(self):
        params = {
            'DATA_URL':     'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv',
            'TRANSPARENT':  'true',
            'FORMAT':       'image/png',
            'SERVICE':      'WMS',
            'VERSION':      '1.1.1',
            'REQUEST':      'GetMap',
            'STYLES':       '',
            'SRS':          'EPSG:3857',
            'BBOX':         '-20037508.34,-10018754.17,-15028131.255,-5009377.085',
            'WIDTH':        '512',
            'HEIGHT':       '512',
            'LAYERS':       'DEFAULT',
        }

        res = self.testapp.get('/api/point/1/wms_data_url', status='*', params=params)
        self.assertEqual(res.status_int, 200)

        self.assertEqual(res.content_type, 'image/png')

    # Lat/Lng Decimal
    def test_view_point_api_wms_srs_epsg_4326(self):
        params = {
            'DATA_URL':     'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv',
            'TRANSPARENT':  'true',
            'FORMAT':       'image/png',
            'SERVICE':      'WMS',
            'VERSION':      '1.1.1',
            'REQUEST':      'GetMap',
            'STYLES':       '',
            'SRS':          'EPSG:4326',
            'BBOX':         '-180,-90,180,90',
            'WIDTH':        '100',
            'HEIGHT':       '100',
            'LAYERS':       'DEFAULT',
        }

        res = self.testapp.get('/api/point/1/wms_data_url', status='*', params=params)
        self.assertEqual(res.status_int, 200)

        self.assertEqual(res.content_type, 'image/png')

    # Lat/Lng Decimal
    def test_view_point_api_wms_srs_epsg_4326_with_absences(self):
        params = {
            'DATA_URL':     'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/absences.csv',
            'TRANSPARENT':  'true',
            'FORMAT':       'image/png',
            'SERVICE':      'WMS',
            'VERSION':      '1.1.1',
            'REQUEST':      'GetMap',
            'STYLES':       '',
            'SRS':          'EPSG:4326',
            'BBOX':         '-180,-90,180,90',
            'WIDTH':        '100',
            'HEIGHT':       '100',
            'LAYERS':       'DEFAULT',
        }

        res = self.testapp.get('/api/point/1/wms_data_url', status='*', params=params)
        self.assertEqual(res.status_int, 200)

        self.assertEqual(res.content_type, 'image/png')

    def test_view_point_api_csv_bad_data_not_a_number(self):
        params = {
            'DATA_URL':     'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/bad_occurrences_lon_values_nan.csv',
            'TRANSPARENT':  'true',
            'FORMAT':       'image/png',
            'SERVICE':      'WMS',
            'VERSION':      '1.1.1',
            'REQUEST':      'GetMap',
            'STYLES':       '',
            'SRS':          'EPSG:4326',
            'BBOX':         '-180,-90,180,90',
            'WIDTH':        '100',
            'HEIGHT':       '100',
            'LAYERS':       'DEFAULT',
        }

        res = self.testapp.get('/api/point/1/wms_data_url', status='*', params=params)
        self.assertEqual(res.status_int, 500)

        self.assertEqual(res.content_type, 'text/html')

    def test_view_point_api_csv_bad_header(self):
        params = {
            'DATA_URL':     'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/bad_occurrences_header.csv',
            'TRANSPARENT':  'true',
            'FORMAT':       'image/png',
            'SERVICE':      'WMS',
            'VERSION':      '1.1.1',
            'REQUEST':      'GetMap',
            'STYLES':       '',
            'SRS':          'EPSG:4326',
            'BBOX':         '-180,-90,180,90',
            'WIDTH':        '100',
            'HEIGHT':       '100',
            'LAYERS':       'DEFAULT',
        }

        res = self.testapp.get('/api/point/1/wms_data_url', status='*', params=params)
        self.assertEqual(res.status_int, 500)

        self.assertEqual(res.content_type, 'text/html')

    def test_wms_view_point_api_csv_with_large_file(self):
        start_t = time.clock()
        params = {
            'DATA_URL':     'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/magpies.csv',
            'TRANSPARENT':  'true',
            'FORMAT':       'image/png',
            'SERVICE':      'WMS',
            'VERSION':      '1.1.1',
            'REQUEST':      'GetMap',
            'STYLES':       '',
            'SRS':          'EPSG:4326',
            'BBOX':         '-180,-90,180,90',
            'WIDTH':        '100',
            'HEIGHT':       '100',
            'LAYERS':       'DEFAULT',
        }

        res = self.testapp.get('/api/point/1/wms_data_url', status='*', params=params)
        end_t = time.clock()
        took = end_t - start_t

        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.content_type, 'image/png')

        self.assertTrue(took < 5, "Time to process large file is too long. Should be less than 5 seconds, took: %f seconds" % took)

    def test_view_point_api_wfs_with_additional_columns(self):
        params = {
            'DATA_URL':     'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences_with_additional_columns.csv',
            'request':      'GetFeature',
            'service':      'WFS',
            'version':      '1.1.0',
            'typeName':     'DEFAULT',
            'outputFormat': 'geojson',
        }
        res = self.testapp.get('/api/point/1/wfs_data_url', status='*', params=params)
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.content_type, 'application/json')

        loaded_json = json.loads(res.body)
        self.assertEqual(type(loaded_json), dict)
        self.assertEqual(loaded_json['type'], 'FeatureCollection')

    # SRS -> Lat/Lng Decimal
    # Get Legend
    def test_view_point_api_wms_srs_epsg_4326_get_legend(self):
        params = {
            'DATA_URL':     'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv',
            'FORMAT':       'image/png',
            'SERVICE':      'WMS',
            'VERSION':      '1.0.0',
            'REQUEST':      'GetLegendGraphic',
            'SRS':          'EPSG:4326',
            'BBOX':         '-180,-90,180,90',
            'WIDTH':        '100',
            'HEIGHT':       '100',
        }

        res = self.testapp.get('/api/point/1/wms_data_url', status='*', params=params)
        self.assertEqual(res.status_int, 200)

        self.assertEqual(res.content_type, 'image/png')
