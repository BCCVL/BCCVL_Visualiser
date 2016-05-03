from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.settings import aslist
import logging
from bccvl_visualiser.auth import AuthTktAuthenticationPolicy
from bccvl_visualiser.models import BCCVLMap
from bccvl_visualiser.models.external_api import DataManager, DatabaseManager
from bccvl_visualiser.models.external_api import FDataMover, DataMover




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

def configure_data_manager(settings):
    """ Configure the Data Manager """
    DataManager.configure_from_config(settings)

def configure_data_mover(settings):
    """ Configure the Data Mover """
    FDataMover.configure_from_config(settings)

def configure_database_manager(settings):
    """ Configure the Database Manager """
    DatabaseManager.configure_from_config(settings)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # TODO: read config from ini file (settings)
    authn_policy = AuthTktAuthenticationPolicy(
        secret=settings['authtkt.secret'],
        callback=None,
        cookie_name=settings['authtkt.name'],
        secure=True,
        timeout=43200,
        reissue_time=21600,
        hashalg='md5',  # the only compatible way ... plone doesn't use hexdigest but pyramid does for other hash algorithms
    )

    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings)

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    # Configure dogpile.cache regions from configuration
    initialise_cache(config.registry.settings)
    # Configure our BCCVL Map class
    configure_bccvl_map(config.registry.settings)
    # Configure our DataManager class
    configure_data_manager(config.registry.settings)
    # Configure our DataMover class
    configure_data_mover(config.registry.settings)
    # Configure the postgis database server
    configure_database_manager(config.registry.settings)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view(name='public_data', path=DataMover.PUBLIC_DIR)

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

    # CSV API
    config.add_route('csv_api_v1', '/api/csv/1*traverse')
    config.add_route('csv_api',    '/api/csv*traverse')

    # PNG API
    config.add_route('png_api_v1', '/api/png/1*traverse')
    config.add_route('png_api',    '/api/png*traverse')

    # HTML API
    config.add_route('html_api_v1', '/api/html/1*traverse')
    config.add_route('html_api',    '/api/html*traverse')

    # ZIP API
    config.add_route('zip_api_v1', '/api/zip/1*traverse')
    config.add_route('zip_api', '/api/zip*traverse')

    # WFS API
    config.add_route('wfs_api_v1', '/api/wfs/1*traverse', factory='bccvl_visualiser.resource.Context')
    config.add_route('wfs_api', '/api/wfs*traverse', factory='bccvl_visualiser.resource.Context')

    # WMS API
    config.add_route('wms_api_v1',  '/api/wms/1*traverse', factory='bccvl_visualiser.resource.Context')
    config.add_route('wms_api',  '/api/wms*traverse', factory='bccvl_visualiser.resource.Context')
    # config.add_route('wms_api_v1',  '/api/wms/1*traverse')
    # config.add_route('wms_api',  '/api/wms*traverse')

    # Auto Detect API
    config.add_route('auto_detect_api_v1', '/api/auto_detect/1*traverse')
    config.add_route('auto_detect_api', '/api/auto_detect*traverse')

    # Base API (API Collection)
    config.add_route('api', '/api*traverse')

    config.scan()
    return config.make_wsgi_app()
