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

    @unittest.skip("WFS GeoJSON response is missing the point with the largest lat and lng value. This is a bug in mapscript")
    def test_create_and_render_wfs_map_via_point_api_v1(self):
        data_url     = "https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv"
        query_string = "request=GetFeature&service=WFS&version=1.1.0&typeName=DEFAULT&outputFormat=geojson"
        my_map = PointAPIv1(data_url=data_url, query_string=query_string)
        map_content, map_content_type, retval = my_map.render()
        expected_content= '''features": [\n    \n    {\n      "type": "Feature",\n      "geometry": {\n        "type": "Point",\n        "coordinates": [32.09, 42.12]\n      },\n      "properties": {\n      }\n    },\n    \n    {\n      "type": "Feature",\n      "geometry": {\n        "type": "Point",\n        "coordinates": [45, 21]\n      },\n      "properties": {\n      }\n    },\n    \n    {\n      "type": "Feature",\n      "geometry": {\n        "type": "Point",\n        "coordinates": [56.43, 43.22]\n      },\n      "properties": {\n      }\n    },\n    \n    {\n      "type": "Feature",\n      "geometry": {\n        "type": "Point",\n        "coordinates": [179, -89.01]\n      },\n      "properties": {\n      }\n    }\n  ]\n}\n\n'''

        self.assertEqual(map_content, expected_content)
        self.assertEqual(map_content_type, "application/json; subtype=geojson")
        self.assertEqual(retval, mapscript.MS_SUCCESS, "Should return success code: %s, but didn't" % mapscript.MS_SUCCESS)
