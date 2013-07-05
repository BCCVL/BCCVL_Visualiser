class BaseAPI(object):

    @staticmethod
    def identifier():
        """Returns the human readable name for this API"""
        raise NotImplementedError("Please Implement this method")

    @staticmethod
    def description():
        """Returns a human readable description for this API"""
        raise NotImplementedError("Please Implement this method")

    @classmethod
    def to_dict(_class):
        """Returns a dict representation of the API

           This dict identifies the API, and its
           general purpose. More specific information about the
           API is defined at the specific version level of the API.
        """
        return_dict = {
            'name':         _class.identifier(),
            'description':  _class.description()
        }

        return return_dict
