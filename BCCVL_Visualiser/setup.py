import os

from setuptools import setup, find_packages

here = os.path.dirname(__file__)

README = open(os.path.join(here, 'README')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'SQLAlchemy',
    #'GDAL >= 1.7.3',       # Better to depend on system installed version
    #'MapScript >= 7.0.0',  # There is no distirbution we can deppend on.. it's either there ore not
    'dogpile.cache',        # cache regions, lets you cache the result of queries
    'requests',
    'pyramid_xmlrpc',
    'futures',
    'org.bccvl.movelib[http]',
]

# FIXME: tests need /tmp/bccvl/mapdata???
tests_require = [
    'mock',
    'nose',
    'webtest',
    'coverage'
]

setup(
    name='BCCVL_Visualiser',
    #setup_requires=['gu_scm_version'],
    #gu_scm_version=True,
    version='1.8.0.dev0',
    description='BCCVL_Visualiser',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='',
    url='',
    keywords='web wsgi bfg pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    extras_require={'test': tests_require},
    entry_points={
        'paste.app_factory': [
            'main = bccvl_visualiser:main'
        ],
    },
)
