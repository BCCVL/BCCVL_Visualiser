import requests

from bccvl_visualiser.models import DEFAULT_PROJECTION

class ALAHelper(object):

    ALA_SPECIES_SERVICE_URL = "http://biocache.ala.org.au/ws/webportal/species"

    @staticmethod
    def ala_search_for_species(species_name):
        """ Searches ALA for the given species
        """
        query_params = { 'q': species_name }
        r = requests.get(ALAHelper.ALA_SPECIES_SERVICE_URL, params=query_params)
        json_data = r.json()
        return json_data

