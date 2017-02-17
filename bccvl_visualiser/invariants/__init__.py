from bccvl_visualiser.exceptions import XORException

def data_id_xor_data_url_invariant(ob):
    """ The object must have either a data_id, or a data_url """
    if ob.data_id and ob.data_url:
        raise XORException( { 'data_id': ob.data_id, 'data_url': ob.data_url } )
    elif ( (not ob.data_id) and (not ob.data_url) ):
        raise XORException( { 'data_id': ob.data_id, 'data_url': ob.data_url } )
