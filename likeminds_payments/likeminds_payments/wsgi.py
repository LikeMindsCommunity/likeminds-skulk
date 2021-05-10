"""
WSGI config for likeminds_payments project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from django.conf import settings

if not settings.IS_BETA:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'likeminds_payments.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lieminds_payments.settings.development')

application = get_wsgi_application()
