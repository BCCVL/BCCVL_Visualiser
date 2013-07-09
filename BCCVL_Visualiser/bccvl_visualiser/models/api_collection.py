from bccvl_visualiser.models.raster_api import *


# Act as a proxy, providing access to the API classes
class APICollection(object):

    @staticmethod
    def to_dict():
        """Returns a dict representation of the api collection"""

        return_dict = {}
        for _class in APICollection.base_api_inheritors():
            return_dict[_class.identifier()] = _class.to_dict()

        return return_dict

    @staticmethod
    def base_api_inheritors():
        """Returns an array of all classes that have implemented BaseAPI"""
        return BaseAPI.__subclasses__()
