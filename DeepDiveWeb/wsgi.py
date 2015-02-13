"""
WSGI config for DeepDiveWeb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os, sys
sys.path.append('/home/iaross/deepdive_site_prd/DeepDive/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'DeepDiveWeb.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
