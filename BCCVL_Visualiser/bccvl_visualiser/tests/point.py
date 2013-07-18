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
