"""
WSGI config for init project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from django.conf import settings

if not settings.IS_BETA:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'init.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'init.settings.beta')

application = get_wsgi_application()
