import unittest
import transaction
import pprint

from pyramid import testing

from bccvl_visualiser.models import *
from bccvl_visualiser.tests import *

pp = pprint.PrettyPrinter(indent=4)

class TestMyCode(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_ala_search(self):
        from bccvl_visualiser.models import (
            ALAHelper,
            )
        json_obj = ALAHelper.ala_search_for_species('kookaburra')
        pp.pprint(json_obj)

        # Check that we found at least 2 species of Kookaburra
        self.assertTrue(len(json_obj) > 2, "Should find at least 2 species of kookaburra")

    def test_api_class_inheritence(self):
        self.assertEqual(BaseRasterAPI.identifier(), 'raster')

    def test_api_collection(self):
        print APICollection.base_api_inheritors()
        self.assertTrue(BaseRasterAPI in APICollection.base_api_inheritors())

    def test_api_collection_to_dict(self):
        api_dict = APICollection.to_dict()
        self.assertEqual(api_dict['raster']['name'], 'raster')

    def test_get_direct_inheritors_version_dict(self):
        """This test will fail if a new version of the Raster API is added"""
        inheritors_version_dict = BaseRasterAPI.get_direct_inheritors_version_dict()

        self.assertEqual(inheritors_version_dict[1], RasterAPIv1)
        self.assertEqual(len(inheritors_version_dict), 1)

    def test_raster_api_v1_map_file_name(self):
        self.assertEqual(RasterAPIv1.MAP_FILE_NAME, 'raster_api_v1_map_file.map')
