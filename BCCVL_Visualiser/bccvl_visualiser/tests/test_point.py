import unittest
import transaction
import pprint

from pyramid import testing

from bccvl_visualiser.models import *

pp = pprint.PrettyPrinter(indent=4)

class TestPointAPIv1(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        pass

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

    def test_point_api_v1_map_file_name(self):
        self.assertEqual(PointAPIv1.MAP_FILE_NAME, 'point_api_v1_map_file.map')

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

    def test_to_dict(self):
        name = PointAPIv1.identifier()
        description = PointAPIv1.description()
        version = PointAPIv1.version()

        the_dict = PointAPIv1.to_dict()

        self.assertEqual(the_dict['name'], name, msg="Name should match")
        self.assertEqual(the_dict['description'], description, msg="Description should match")
        self.assertEqual(the_dict['version'], version, msg="Version should match")
