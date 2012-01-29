# Django global settings

import os
PROJECT = os.path.dirname(__file__)

TEST_RUNNER='django.contrib.gis.tests.run_gis_tests'

DEBUG=True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_NAME = 'geoadmin'
DATABASE_USER = '' # make sure to change this to your postgres user
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

DATABASES = {
    'default': {
        'NAME': DATABASE_NAME,
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'USER': DATABASE_USER,
        'PASSWORD': ''
    }
}

GOOGLE_MAPS_API_KEY='abcdefg'

GIS_DATA_DIR = os.path.join(PROJECT, 'data')

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Vancouver'

SITE_ID = 1

USE_I18N = True

MEDIA_ROOT = os.path.join(PROJECT, 'media')

MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = '/admin_media/'

SECRET_KEY = '2f!vq4!f)u#g-sk7_=z+i0e(o0o&hue5khxbdkdx$f%hvpb^vd'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.load_template_source',
)

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
TEMPLATE_CONTEXT_PROCESSORS += (
     'django.core.context_processors.request',
) 

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.databrowse',
    'django.contrib.gis',
    'world',
    'djmapnik'
)
