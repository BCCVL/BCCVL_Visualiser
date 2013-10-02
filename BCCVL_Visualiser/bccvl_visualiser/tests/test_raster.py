
import unittest
import transaction
import pprint

from pyramid import testing

from bccvl_visualiser.models import *

pp = pprint.PrettyPrinter(indent=4)

class TestRasterAPIv1(unittest.TestCase):

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

    def test_raster_api_v1_map_file_name(self):
        self.assertEqual(RasterAPIv1.MAP_FILE_NAME, 'raster_api_v1_map_file.map')

    def test_raster_api_identifier(self):
        self.assertEqual(BaseRasterAPI.identifier(), 'raster')


