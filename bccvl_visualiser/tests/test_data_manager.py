import unittest

from bccvl_visualiser.models import *

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

    def test_data_manager_base_url(self):
        self.assertEqual(DataManager.BASE_URL, self.config['bccvl.data_manager.base_url'])

    def test_new_data_manager_raises_on_bad_args(self):
        with self.assertRaises(ValueError):
            DataManager()
        with self.assertRaises(ValueError):
            DataManager(data_id="111", data_url="http://example.com")

    def test_new_data_manager_from_data_id(self):
        # This isn't implemented yet
        with self.assertRaises(NotImplementedError):
            my_map = DataManager(data_id="908h08h")
