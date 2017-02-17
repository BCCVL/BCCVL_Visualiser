from os import path
from codecs import open
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))


def read(fname):
    open(path.join(here, fname), encoding='utf-8').read()


long_description = '\n'.join((
    read('README.rst'),
    read('CHANGES.rst')
))

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_tm',
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
    setup_requires=['guscmversion'],
    guscmversion=True,
    description='BCCVL_Visualiser',
    long_description=long_description,
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
