from setuptools import setup

__version__ = '0.0.1'

REQUIRES = ['psycopg2-binary']
TESTS_REQUIRES = []
EXTRAS_REQUIRES = {}

setup_dict = dict(name='dbactor',
                  version=__version__,
                  description='DBActor',
                  long_description=open('README.md').read(),
                  url='http://github.com/jackschultz/dbactor',
                  author='Jack Schultz',
                  author_email='jackschultz23@gmail.com',
                  license='MIT',
                  install_requires=REQUIRES,
                  extras_requires=EXTRAS_REQUIRES,
                  tests_requires=TESTS_REQUIRES,
                  packages=['dbactor'])


setup(**setup_dict)