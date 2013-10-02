import unittest
import transaction
import pprint

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

        # Get the file path
        fp = my_map.map_file_path
        self.assertEqual(type(fp), str)

        # Get the number of layers
        self.assertEqual(my_map.numlayers, 1)
