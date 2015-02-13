#Embedded file name: /home/iaross/deepdive_site_prd/DeepDive/DeepDiveWeb/settings.py
"""
Django settings for DeepDiveWeb project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
import ConfigParser
import pdb
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

config = ConfigParser.RawConfigParser()
config.read(BASE_DIR + '/deepdiveweb.cfg')

secret_key = config.get('django', 'secret_key')
dbuser = config.get('database', 'user')
dbpassword = config.get('database', 'password')

SECRET_KEY = secret_key

DEBUG = True

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['http://deepdivesubmit.chtc.wisc.edu/']

INSTALLED_APPS = ('django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'django_mongodb_engine')

MIDDLEWARE_CLASSES = ('django.middleware.common.CommonMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.contrib.messages.middleware.MessageMiddleware')

ROOT_URLCONF = 'DeepDiveWeb.urls'

WSGI_APPLICATION = 'DeepDiveWeb.wsgi.application'

DATABASES = {'default': {'ENGINE': 'django_mongodb_engine',
    'NAME': 'site_db',
    'USER': dbuser,
    'PASSWORD': dbpassword,
    'HOST': '',
    'PORT': ''}}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'

STATICFILES_FINDERS = ('django.contrib.staticfiles.finders.FileSystemFinder', 'django.contrib.staticfiles.finders.AppDirectoriesFinder')
