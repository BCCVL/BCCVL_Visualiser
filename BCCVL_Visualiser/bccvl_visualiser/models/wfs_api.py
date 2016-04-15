from bccvl_visualiser.models.api import BaseAPI


class WFSAPI(BaseAPI):

    @staticmethod
    def identifier():
        return "wfs"

    @staticmethod
    def description():
        desc = "Serve shape files as WFS."
        return desc


class WFSAPIv1(WFSAPI):

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
        super(WFSAPIv1, self).__init__(**kwargs)
