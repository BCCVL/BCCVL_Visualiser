import bccvl_visualiser
from bccvl_visualiser.models.external_api.data_mover import LocalDataMover

import tempfile
import os

# Save the DataMover to _DataMover
bccvl_visualiser.models.external_api.data_mover._DataMover = bccvl_visualiser.models.external_api.DataMover
# Overwrite the DataMover with the LocalDataMover
bccvl_visualiser.models.external_api.data_mover.DataMover = LocalDataMover

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

    def test_move_file_successfully_status(self):
        tmp = tempfile.gettempdir()
        tmp_file_path = os.path.join(tmp, 'hello_world.html')
        url = 'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/hello_world.html'

        # Delete the file (if it exists)
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

        # Create a DataMover object to move the file to the dest file path
        mover = DataMover(tmp_file_path, data_url=url)
        move_output = mover.move_file()

        move_job_id = move_output['id']
        self.assertTrue(isinstance(move_job_id, int))
        self.assertEqual(move_job_id, mover.job_id)

        move_status = mover.get_status()

        self.assertEqual(move_status['status'], 'COMPLETE')
        self.assertEqual(move_status['id'], move_job_id)
