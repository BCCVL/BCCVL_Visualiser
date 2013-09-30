import unittest
import transaction
import pprint

from pyramid import testing

from bccvl_visualiser.models import *

pp = pprint.PrettyPrinter(indent=4)

class TestAPICollection(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        pass

    def test_api_collection(self):
        base_api_inheritors = APICollection.base_api_inheritors()
        self.assertEqual(type(base_api_inheritors), list)

    def test_api_collection_to_dict(self):
        api_dict = APICollection.to_dict()
        self.assertEqual(type(api_dict), dict)
