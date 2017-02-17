import unittest

from pyramid import testing


class TestMyCode(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        pass

    def test_test_env_working(self):
        self.assertEqual(True, True)
