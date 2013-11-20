import bccvl_visualiser
from bccvl_visualiser.models.external_api.data_mover import TestDataMover

# Save the DataMover to _DataMover
bccvl_visualiser.models.external_api.data_mover._DataMover = bccvl_visualiser.models.external_api.DataMover
# Overwrite the DataMover with the TestDataMover
bccvl_visualiser.models.external_api.data_mover.DataMover = TestDataMover

from bccvl_visualiser.models.external_api.data_mover import DataMover, _DataMover

import unittest
import transaction
import pprint
import types

from pyramid import testing


pp = pprint.PrettyPrinter(indent=4)

from paste.deploy.loadwsgi import appconfig

class TestBCCVLMap(unittest.TestCase):

    def setUp(self):
        self.config = appconfig('config:development.ini', 'pyramid', relative_to='.')
        from bccvl_visualiser import main
        app = main(None, **self.config)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        pass

    def test_data_mover_base_url(self):
        self.assertEqual(DataMover.BASE_URL, self.config['bccvl.data_mover.base_url'])

    def test_new_data_mover_raises_on_bad_args(self):
        with self.assertRaises(ValueError):
            DataMover('/tmp/a.csv')
        with self.assertRaises(ValueError):
            DataMover('/tmp/a.csv', data_id="111", data_url="http://example.com")

    def test_new_data_mover_from_data_id(self):
        # This isn't implemented yet
        with self.assertRaises(NotImplementedError):
            my_map = DataMover('tmp/a.csv', data_id="908h08h")
