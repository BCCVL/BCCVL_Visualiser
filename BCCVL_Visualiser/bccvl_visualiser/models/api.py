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

    @staticmethod
    def version():
        """Returns the version of this API (as an integer)"""
        raise NotImplementedError("Please Implement this method")

    @classmethod
    def get_direct_inheritors_version_dict(_class):
        """Returns a dict of version to api class

            {
                1: API_Class_V1,
                2: API_Class_V2
            }
        """
        inheritors = _class.__subclasses__()
        return_dict = {}
        for inheritor in inheritors:
            return_dict[inheritor.version()] = inheritor

        return return_dict

    @classmethod
    def get_human_readable_inheritors_version_dict(_class):
        """Returns a human readable dict of version to api information

            {
                1: {
                    'name': raster,
                    'description': this is the raster API v1,
                },
                2: {
                    'name': raster,
                    'description': this is the raster API v2,
                }
            }
        """
        inheritors = _class.__subclasses__()
        return_dict = {}
        for inheritor in inheritors:
            return_dict[inheritor.version()] = inheritor.to_dict()

        return return_dict

    @classmethod
    def API_class_for_version(_class, version):
        """Given a version number, will return the appropriate API"""
        inheritors_version_dict = _class.get_direct_inheritors_version_dict()

        return inheritors_version_dict[version]
