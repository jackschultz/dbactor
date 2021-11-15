from setuptools import setup

__version__ = '0.0.3'

REQUIRES = ['psycopg2-binary']
EXTRAS_REQUIRE = {
    'sqlalchemy': ['sqlalchemy'],
    'jinjasql': ['jinjasql'],
    'pandas': ['jinjasql', 'pandas'],
}
extras_lists = [vals for k, vals in EXTRAS_REQUIRE.items()]
# flattening the values in EXTRAS_REQUIRE from popular stack overflow question 952914
all_extras_require = list(set([item for sublist in extras_lists for item in sublist]))
EXTRAS_REQUIRE['all'] = all_extras_require
TESTS_REQUIRE = REQUIRES + all_extras_require + ['pytest', 'testing.postgresql']

setup_dict = dict(name='dbactor',
                  version=__version__,
                  description='DBActor: ORM helper and alternative',
                  long_description=open('README.md').read(),
                  url='http://github.com/jackschultz/dbactor',
                  author='Jack Schultz',
                  author_email='jackschultz23@gmail.com',
                  license='MIT',
                  install_requires=REQUIRES,
                  extras_require=EXTRAS_REQUIRE,
                  tests_require=TESTS_REQUIRE,
                  packages=['dbactor'])


setup(**setup_dict)
