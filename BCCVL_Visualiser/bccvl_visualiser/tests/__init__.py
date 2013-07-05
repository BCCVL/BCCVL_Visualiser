import unittest
import transaction
import pprint

from pyramid import testing

from bccvl_visualiser.models import *

from sqlalchemy import create_engine

pp = pprint.PrettyPrinter(indent=4)

class TestMyCode(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine

        engine = create_engine('postgresql+psycopg2://pyramid:pyramid_password@localhost:5432/pyramid_test_db')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            # Create a species
            species             = Species(name='Kookaburra')
            # Add its occurrences
            species.occurrences = [
                Occurrence("POINT(30 10)"),
                Occurrence("POINT(20 10)"),
                ]

            DBSession.add(species)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

        engine = create_engine('postgresql+psycopg2://pyramid:pyramid_password@localhost:5432/pyramid_test_db')
        DBSession.configure(bind=engine)
        # Drop all the models
        Base.metadata.drop_all(engine)

    def test_search_species_db_by_name(self):
        kookaburra = DBSession.query(Species).\
            filter_by(name='Kookaburra').one()
        self.assertEqual(kookaburra.name, 'Kookaburra')
        self.assertEqual(len(kookaburra.occurrences), 2)

    def test_ala_search(self):
        from bccvl_visualiser.models import (
            Species,
            )
        json_obj = Species.ala_search_for_species('kookaburra')
        pp.pprint(json_obj)

        # Check that we found at least 2 species of Kookaburra
        self.assertTrue(len(json_obj) > 2, "Should find at least 2 species of kookaburra")

    def test_api_class_inheritence(self):
        self.assertEqual(RasterAPI.identifier(), 'raster')

    def test_api_collection(self):
        print APICollection.API_CLASSES
        self.assertTrue(RasterAPI in APICollection.API_CLASSES)

    def test_api_collection_to_dict(self):
        api_dict = APICollection.to_dict()
        print api_dict
        self.assertEqual(api_dict['raster']['name'], 'raster')
