import os
from setuptools import setup, find_packages

VERSION = '0.0.1b'

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-haystack-channels',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    license='TDB Licence',
    description='Helper code to connect Haystack to Django Channels',
    long_description=README,
    url='https://github.com/LegoStormtroopr/django-haystack-channels',
    author='Samuel Spencer',
    author_email='sam@aristotlemetadata.com',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',

        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires = [
        "Django",
        'channels',
        'django-haystack',
    ],

)
