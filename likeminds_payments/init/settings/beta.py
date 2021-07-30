from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('BETA_DB_NAME'),
        'USER': os.getenv('BETA_DB_USER'),
        'PASSWORD': os.getenv('BETA_DB_PASSWORD'),
        'HOST': os.getenv('BETA_DB_HOST'),
        'PORT': '5432',
        'CONN_MAX_AGE': 600
    }
}

TIME_ZONE = 'Asia/Kolkata'

# variable to check for beta server
IS_BETA = True

URL = os.getenv("BETA_URL")
CORE_SERVICE_URL = os.getenv("BETA_CORE_URL")

ALLOWED_HOSTS = [os.getenv("BETA_ALLOWED_HOST_1"), os.getenv("BETA_ALLOWED_HOST_2")]

RAZORPAY_KEY = os.getenv("BETA_RAZORPAY_KEY")
RAZORPAY_SECRET = os.getenv("BETA_RAZORPAY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("BETA_RAZORPAY_WEBHOOK_SECRET")

SEGMENT_KEY = os.getenv("BETA_SEGMENT_KEY")

CRONTAB_DJANGO_SETTINGS_MODULE = 'init.settings.beta'

FB_ACCESS_TOKEN = os.getenv("BETA_FB_ACCESS_TOKEN")
FB_PIXEL_ID = os.getenv("BETA_FB_PIXEL_ID")

USE_INTERNAL_FILE_LOGGER = False
OMIT_200_OK_FULL_RESPONSE = False

CORALOGIX_LOGGER = {
    'PRIVATE_API_KEY': os.getenv('BETA_CORALOGIX_LOGGER_PRIVATE_API_KEY'),
    'APPLICATION_NAME': 'LM-SUBSCRIPTIONS-BETA',
    'SUBSYSTEM_NAME_API': 'Backend_App_Api',
    'SUBSYSTEM_NAME_APP': 'Backend_App_System'
}
