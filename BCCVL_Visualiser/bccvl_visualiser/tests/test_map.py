import unittest
import transaction
import pprint
import mapscript

from pyramid import testing

from bccvl_visualiser.models import *

pp = pprint.PrettyPrinter(indent=4)

from paste.deploy.loadwsgi import appconfig


class TestPointAPIv1(unittest.TestCase):
    def setUp(self):
        self.config = appconfig('config:development.ini', 'pyramid', relative_to='.')
        from bccvl_visualiser import main
        app = main(None, **self.config)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        pass

    def test_new_bccvl_map_raises_on_bad_args(self):
        with self.assertRaises(ValueError):
            OccurrencesBCCVLMap()
        with self.assertRaises(ValueError):
            OccurrencesBCCVLMap(data_id="111", data_url="http://example.com")

    def test_new_bccvl_map_from_data_url(self):
        # This shouldn't die...
        my_map = OccurrencesBCCVLMap(data_url="https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv")

    def test_new_bccvl_map_from_data_url_file_exists(self):
        # This shouldn't die...
        my_map = OccurrencesBCCVLMap(data_url="https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv")
        # This should make a second map with the same file path
        my_map_2 = OccurrencesBCCVLMap(data_url="https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv")

        # Get the data file's path
        fp = my_map.data_file_path
        self.assertEqual(type(fp), str, "file path should be a string")
        self.assertTrue(os.path.isfile(fp), "file should exist on disk")

        fp_2 = my_map_2.data_file_path
        self.assertEqual(fp, fp_2, "The same URL should download to the same file")

        # delete the file
        os.remove(fp)
        self.assertFalse(os.path.isfile(fp), "file should no longer exist on disk")

        my_map_3 = OccurrencesBCCVLMap(data_url="https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv")
        fp_3 = my_map_3.data_file_path

        self.assertEqual(fp, fp_3, "The same URL should download to the same file")
        self.assertTrue(os.path.isfile(fp_3), "file should exist on disk")

    def test_new_bccvl_map_from_data_url_layer_exists(self):
        # This shouldn't die...
        my_map = OccurrencesBCCVLMap(data_url="https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv")

        # Get the number of layers
        self.assertEqual(my_map.numlayers, 1)

        # Layer data should be None for a Occurrences Layer
        layer_name = my_map.layer_name
        layer = my_map.getLayerByName(layer_name)
        self.assertEqual(layer.data, None, "layer.data should be None. If it's not, it will override the Map's CONNECTION")

    def test_new_bccvl_map_from_data_url_with_query_string(self):
        # This shouldn't die...
        my_map = OccurrencesBCCVLMap(data_url="https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv", query_string="HEIGHT=1024&LAYERS=DEFAULT&WIDTH=512")
        self.assertEqual(my_map.ows_request.getValueByName('HEIGHT'), '1024')
        self.assertEqual(my_map.ows_request.getValueByName('WIDTH'), '512')

    def test_new_bccvl_map_render(self):
        # This shouldn't die...
        my_map = OccurrencesBCCVLMap(data_url="https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/occurrences.csv", query_string="TRANSPARENT=true&FORMAT=image%2Fpng&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&STYLES=&SRS=EPSG%3A3857&BBOX=-20037508.34,-10018754.17,-15028131.255,-5009377.085&WIDTH=512&HEIGHT=1024&LAYERS=DEFAULT")
        # Our height, width, etc. should now be applied
        self.assertEqual(my_map.ows_request.getValueByName('HEIGHT'), '1024')
        self.assertEqual(my_map.ows_request.getValueByName('WIDTH'), '512')

        map_image, map_image_content_type, mapscript_return_code = my_map.render()
        self.assertEqual(map_image_content_type, "image/png")
        self.assertEqual(mapscript_return_code, mapscript.MS_SUCCESS, "Should return success code: %s, but didn't" % mapscript.MS_SUCCESS)

    def test_new_bccvl_map_from_data_id(self):
        # This isn't implemented yet
        with self.assertRaises(NotImplementedError):
            my_map = OccurrencesBCCVLMap(data_id="908h08h")
