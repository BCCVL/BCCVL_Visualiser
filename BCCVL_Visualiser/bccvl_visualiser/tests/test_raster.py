
import unittest
import transaction
import pprint
import json

from pyramid import testing

from bccvl_visualiser.models import BaseRasterAPI, RasterAPIv1, APICollection, DataMoverF

from paste.deploy.loadwsgi import appconfig

pp = pprint.PrettyPrinter(indent=4)

class TestRasterAPIv1(unittest.TestCase):

    def setUp(self):
        DataMoverF.LOCAL = True

        self.config = appconfig('config:development.ini', 'pyramid', relative_to='.')
        from bccvl_visualiser import main
        app = main(None, **self.config)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        DataMoverF.LOCAL = False

    def test_raster_in_api_collection(self):
        self.assertTrue(BaseRasterAPI in APICollection.base_api_inheritors())

    def test_point_in_api_collection_to_dict(self):
        api_dict = APICollection.to_dict()
        self.assertEqual(api_dict['raster']['name'], 'raster')

    def test_raster_direct_inheritors_version_dict(self):
        """This test will fail if a new version of the Raster API is added"""
        inheritors_version_dict = BaseRasterAPI.get_direct_inheritors_version_dict()

        self.assertEqual(inheritors_version_dict[1], RasterAPIv1)
        self.assertEqual(len(inheritors_version_dict), 1)

    def test_raster_api_identifier(self):
        self.assertEqual(BaseRasterAPI.identifier(), 'raster')

    def test_view_raster_api_html(self):
       res = self.testapp.get('/api/raster', status='*')
       self.assertEqual(res.status_int, 200)

    def test_view_raster_api_v1_html(self):
       res = self.testapp.get('/api/raster/1', status='*')
       self.assertEqual(res.status_int, 200)

    def test_view_raster_api_v1_json(self):
       res = self.testapp.get('/api/raster/1.json', status='*')
       self.assertEqual(res.status_int, 200)

       loaded_json = json.loads(res.body)
       self.assertEqual(loaded_json['version'], RasterAPIv1.version())
       self.assertEqual(loaded_json['name'], RasterAPIv1.identifier())

    def test_view_raster_api_v1_json(self):
       res = self.testapp.get('/api/raster/bad_version.json', status='*')
       self.assertEqual(res.status_int, 404)

    def test_view_raster_api_v1_json(self):
       res = self.testapp.get('/api/raster/1.json', status='*')
       self.assertEqual(res.status_int, 200)

       loaded_json = json.loads(res.body)
       self.assertEqual(loaded_json['version'], RasterAPIv1.version())
       self.assertEqual(loaded_json['name'], RasterAPIv1.identifier())

    # SRS -> Spherical Mercator
    def test_view_raster_api_wms_srs_epsg_3857(self):
        params = {
            'DATA_URL':     'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/raster.tif',
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

        res = self.testapp.get('/api/raster/1/wms_data_url', status='*', params=params)
        self.assertEqual(res.status_int, 200)

        self.assertEqual(res.content_type, 'image/png')

    # SRS -> Lat/Lng Decimal
    def test_view_raster_api_wms_srs_epsg_4326(self):
        params = {
            'DATA_URL':     'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/raster.tif',
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

        res = self.testapp.get('/api/raster/1/wms_data_url', status='*', params=params)
        self.assertEqual(res.status_int, 200)

        self.assertEqual(res.content_type, 'image/png')
