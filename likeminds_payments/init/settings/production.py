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
WEB_URL = os.getenv('PRODUCTION_WEB_URL')

ALLOWED_HOSTS = [os.getenv("PRODUCTION_ALLOWED_HOST_1"), os.getenv("PRODUCTION_ALLOWED_HOST_2")]

RAZORPAY_KEY = os.getenv("PRODUCTION_RAZORPAY_KEY")
RAZORPAY_SECRET = os.getenv("PRODUCTION_RAZORPAY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("PRODUCTION_RAZORPAY_WEBHOOK_SECRET")

RAZORPAY_X_KEY = os.getenv("PRODUCTION_RAZORPAY_X_KEY")
RAZORPAY_X_SECRET = os.getenv("PRODUCTION_RAZORPAY_X_SECRET")

SEGMENT_KEY = os.getenv("PRODUCTION_SEGMENT_KEY")

CRONTAB_DJANGO_SETTINGS_MODULE = 'init.settings.production'

FB_ACCESS_TOKEN = os.getenv("PRODUCTION_FB_ACCESS_TOKEN")
FB_PIXEL_ID = os.getenv("PRODUCTION_FB_PIXEL_ID")

USE_INTERNAL_FILE_LOGGER = False
OMIT_200_OK_FULL_RESPONSE = True

CORALOGIX_LOGGER = {
    'PRIVATE_API_KEY': os.getenv('PRODUCTION_CORALOGIX_LOGGER_PRIVATE_API_KEY'),
    'APPLICATION_NAME': 'LM-SUBSCRIPTIONS-PROD',
    'SUBSYSTEM_NAME_API': 'Backend_App_Api',
    'SUBSYSTEM_NAME_APP': 'Backend_App_System'
}

AWS_CREDENTIALS = {
    'ACCESS_KEY': os.getenv('PRODUCTION_AWS_S3_ACCESS_KEY'),
    'SECRET_KEY': os.getenv('PRODUCTION_AWS_S3_SECRET_KEY')
}

S3_BUCKETS = {
    'media_bucket': {
        'arn': 'arn:aws:s3:::prod-likeminds-media',
        'name': 'prod-likeminds-media',
        'region': 'ap-south-1'
    }
}
