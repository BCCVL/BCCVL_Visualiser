import unittest
import transaction
import pprint

from pyramid import testing

from bccvl_visualiser.models import *

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

    def test_data_manager_base_url(self):
        self.assertEqual(DataManager.BASE_URL, self.config['bccvl.data_manager.base_url'])
