import unittest

from bccvl_visualiser.models import BaseRAPI, RAPIv1, APICollection
from paste.deploy.loadwsgi import appconfig


class TestRAPIv1(unittest.TestCase):

    def setUp(self):
        self.config = appconfig('config:development.ini', 'pyramid', relative_to='.')
        from bccvl_visualiser import main
        app = main(None, **self.config)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        pass

    def test_view_r_api_r(self):
        res = self.testapp.get('/api/r', status='*')
        self.assertEqual(res.status_int, 200)

    def test_view_r_api_v1_r(self):
        res = self.testapp.get('/api/r/1', status='*')
        self.assertEqual(res.status_int, 200)

    def test_test_env_working(self):
        self.assertEqual(True, True)

    def test_r_in_api_collection(self):
        self.assertTrue(BaseRAPI in APICollection.base_api_inheritors())

    def test_r_in_api_collection_to_dict(self):
        api_dict = APICollection.to_dict()
        self.assertEqual(api_dict['r']['name'], 'r')

    def test_r_direct_inheritors_version_dict(self):
        """This test will fail if a new version of the R API is added"""
        inheritors_version_dict = BaseRAPI.get_direct_inheritors_version_dict()

        self.assertEqual(inheritors_version_dict[1], RAPIv1)
        self.assertEqual(len(inheritors_version_dict), 1)

    def test_r_api_identifier(self):
        self.assertEqual(BaseRAPI.identifier(), 'r')

    def test_version(self):
        self.assertEqual(RAPIv1.version(), 1, msg="Version should be 1")

    def test_to_dict(self):
        name = RAPIv1.identifier()
        description = RAPIv1.description()
        version = RAPIv1.version()

        the_dict = RAPIv1.to_dict()

        self.assertEqual(the_dict['name'], name, msg="Name should match")
        self.assertEqual(the_dict['description'], description, msg="Description should match")
        self.assertEqual(the_dict['version'], version, msg="Version should match")

    def test_view_r_api_v1_data_url_view(self):
        params = {
            'data_url': 'https://raw.github.com/BCCVL/BCCVL_Visualiser/master/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/hello_world.r',
        }

        res = self.testapp.get('/api/r/1/data_url_view', status='*', params=params)

        expected_content = """
<!DOCTYPE html>
<html style="width:100%; height:100%">

    <head>
        <title>R V1 View</title>
        <link href="http://localhost/static/bccvl.css" rel="stylesheet" type="text/css">
        <link href="http://localhost/static/js/rainbow/themes/tricolore.css" rel="stylesheet" type="text/css">
        <script src="http://localhost/static/js/rainbow/rainbow.js"></script>
        <script src="http://localhost/static/js/rainbow/language/r.js"></script>
    </head>

    <body>
        <pre id="file_content">
            <code data-language="r">
cat('Hello, world!\\n')

            </code>
        </pre>

    </body>
</html>
"""

        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.content_type, 'text/html')
        self.assertEqual(res.body.strip(), expected_content.strip())
