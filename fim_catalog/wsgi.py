"""
WSGI config for fim_catalog project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# Add this file path to sys.path in order to import settings
#sys.path.insert(0, os.path.normpath(os.path.join(
#    os.path.dirname(os.path.realpath(__file__)), '../..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fim_catalog.settings")

application = get_wsgi_application()
