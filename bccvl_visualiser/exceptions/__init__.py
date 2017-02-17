import zope.interface

class XORException(zope.interface.Invalid):
    """ An instance has failed an XOR test on its arguments """
    def __repr__(self):
        return "XORException(%r)" % self.args
