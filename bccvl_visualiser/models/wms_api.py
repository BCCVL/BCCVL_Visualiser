from bccvl_visualiser.models.api import BaseAPI


class WMSAPI(BaseAPI):

    @staticmethod
    def identifier():
        return "wms"

    @staticmethod
    def description():
        desc = "Serve raster files as WMS."
        return desc


class WMSAPIv1(WMSAPI):

    @staticmethod
    def version():
        return 1

    @classmethod
    def to_dict(_class):
        """ Returns a dict representation of the API

            This dict identifies the API, and its
            general purpose. More specific information about the
            API is defined at the specific version level of the API.
        """
        return_dict = {
            'name':         _class.identifier(),
            'description':  _class.description(),
            'version': _class.version()
        }

        return return_dict

    def __init__(self, **kwargs):
        """ init the instance """
        super(WMSAPIv1, self).__init__(**kwargs)
