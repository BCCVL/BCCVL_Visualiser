from datetime import timedelta, date, datetime, time
import math

from dogpile.cache import make_region


short_term = make_region()
long_term = make_region()
until_update = make_region()
forever = make_region()

def cache_until(until):
    """Determine total seconds from now until given datetime.
    """
    diff = datetime.datetime.now() - until
    return math.ceil(diff.total_seconds())

