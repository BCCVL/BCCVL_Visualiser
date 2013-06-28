import unittest
import transaction
import pprint

from pyramid import testing

from webapp.models import DBSession

pp = pprint.PrettyPrinter(indent=4)


class TestMyCode(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine

	# Modify the engine to use a test DB
        engine = create_engine('sqlite://')
        from webapp.models import (
            Base,
            Species,
            Occurrence,
            )
        DBSession.configure(bind=engine)
#        Base.metadata.create_all(engine)
#        with transaction.manager:
#            species_model     = Species(name='one')
#            occurrences_model = Occurrence(species_model, "POINT (30 10)")
#            DBSession.add(species_model)
#            DBSession.add(occurrences_model)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

#    def test_it(self):
#        from webapp.views import my_view
#        request = testing.DummyRequest()
#        info = my_view(request)
#        self.assertEqual(info['one'].name, 'Kookaburra')
#        self.assertEqual(info['project'], 'WebApp')

    def test_ala_search(self):
        from webapp.models import (
            Species,
            )
        json_obj = Species.ala_search_for_species('kookaburra')
	pp.pprint(json_obj)

	# Check that we found at least 2 species of Kookaburra
        self.assertTrue(len(json_obj) > 2, "Should find at least 2 species of kookaburra")
