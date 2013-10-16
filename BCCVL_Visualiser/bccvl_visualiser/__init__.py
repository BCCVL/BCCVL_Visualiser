from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.settings import asbool, aslist
import logging
from bccvl_visualiser.models import BCCVLMap

def initialise_cache(settings):
    """ Initialise the application's cache regions
    """

    log = logging.getLogger(__name__)

    from bccvl_visualiser import cache as cache_module

    settings['cache.regions'] = aslist(settings['cache.regions'])
    for cache_name in settings['cache.regions']:
        cache = getattr(cache_module, cache_name)
        if 'backend' not in cache.__dict__:
            prefix = 'cache.{}.'.format(cache_name)
            expiration_time_key = prefix + 'expiration_time'
            if expiration_time_key in settings:
                settings[expiration_time_key] = \
                        int(settings[expiration_time_key])
            cache.configure_from_config(settings, prefix)
        else:
            log.warn('Cache {} is already configured.'.format(cache))

def configure_bccvl_map(settings):
    """ Configure the BCCVL Map """
    BCCVLMap.configure_from_config(settings)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    config = Configurator(settings=settings)

    # Configure dogpile.cache regions from configuration
    initialise_cache(config.registry.settings)
    # Configure our BCCVL Map class
    configure_bccvl_map(config.registry.settings)

    config.add_static_view('static', 'static', cache_max_age=3600)

    # Application routes
    config.add_route('home', '/')

    # Raster API
    config.add_route('raster_api_v1', '/api/raster/1*traverse')
    config.add_route('raster_api', '/api/raster*traverse')

    # Point API
    config.add_route('point_api_v1', '/api/point/1*traverse')
    config.add_route('point_api', '/api/point*traverse')

    # R API
    config.add_route('r_api_v1', '/api/r/1*traverse')
    config.add_route('r_api',    '/api/r*traverse')

    # Base API (API Collection)
    config.add_route('api', '/api*traverse')

    config.scan()
    return config.make_wsgi_app()
