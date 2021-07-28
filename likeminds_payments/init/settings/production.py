from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('PRODUCTION_DB_NAME'),
        'USER': os.getenv('PRODUCTION_DB_USER'),
        'PASSWORD': os.getenv('PRODUCTION_DB_PASSWORD'),
        'HOST': os.getenv('PRODUCTION_DB_HOST'),
        'PORT': '5432',
        'CONN_MAX_AGE': 600
    }
}

TIME_ZONE = 'Asia/Kolkata'

# variable to check for beta server
IS_BETA = False

URL = os.getenv("PRODUCTION_URL")
CORE_SERVICE_URL = os.getenv("PRODUCTION_CORE_URL")

ALLOWED_HOSTS = [os.getenv("PRODUCTION_ALLOWED_HOST_1"), os.getenv("PRODUCTION_ALLOWED_HOST_2")]

RAZORPAY_KEY = os.getenv("PRODUCTION_RAZORPAY_KEY")
RAZORPAY_SECRET = os.getenv("PRODUCTION_RAZORPAY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("PRODUCTION_RAZORPAY_WEBHOOK_SECRET")

SEGMENT_KEY = os.getenv("PRODUCTION_SEGMENT_KEY")

CRONTAB_DJANGO_SETTINGS_MODULE = 'init.settings.production'

FB_ACCESS_TOKEN = os.getenv("PRODUCTION_FB_ACCESS_TOKEN")
FB_PIXEL_ID = os.getenv("PRODUCTION_FB_PIXEL_ID")
