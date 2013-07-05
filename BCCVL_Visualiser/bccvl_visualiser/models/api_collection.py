from bccvl_visualiser.models.raster_api import (
    RasterAPI
    )


# Act as a proxy, providing access to the API classes
class APICollection(object):
    API_CLASSES = [
        RasterAPI
    ]

    @staticmethod
    def to_dict():
        """Returns a dict representation of the api collection"""

        return_dict = {}
        for _class in APICollection.API_CLASSES:
            return_dict[_class.identifier()] = _class.to_dict()

        return return_dict
