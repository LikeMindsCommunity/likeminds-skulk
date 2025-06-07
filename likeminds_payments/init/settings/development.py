import os

from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DEVELOPMENT_DB_NAME'),
        'USER': os.getenv('DEVELOPMENT_DB_USER'),
        'PASSWORD': os.getenv('DEVELOPMENT_DB_PASSWORD'),
        'HOST': os.getenv('DEVELOPMENT_DB_HOST'),
        'PORT': '5432',
        'CONN_MAX_AGE': 600
    }
}

TIME_ZONE = 'Asia/Kolkata'

# variable to check for beta server
IS_BETA = True

URL = os.getenv("DEVELOPMENT_URL")
CORE_SERVICE_URL = os.getenv("DEVELOPMENT_CORE_URL")
WEB_URL = os.getenv('DEVELOPMENT_WEB_URL')
KETTLE_SERVICE_URL = os.getenv("DEVELOPMENT_KETTLE_URL")

ALLOWED_HOSTS = [os.getenv("DEVELOPMENT_ALLOWED_HOST_1"), os.getenv("DEVELOPMENT_ALLOWED_HOST_2")]

RAZORPAY_KEY = os.getenv("DEVELOPMENT_RAZORPAY_KEY")
RAZORPAY_SECRET = os.getenv("DEVELOPMENT_RAZORPAY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("DEVELOPMENT_RAZORPAY_WEBHOOK_SECRET")

RAZORPAY_X_KEY = os.getenv("DEVELOPMENT_RAZORPAY_X_KEY")
RAZORPAY_X_SECRET = os.getenv("DEVELOPMENT_RAZORPAY_X_SECRET")
RAZORPAY_X_ACCOUNT_NUMBER = os.getenv("DEVELOPMENT_RAZORPAY_X_ACCOUNT_NUMBER")
RAZORPAY_X_WEBHOOK_SECRET = os.getenv("DEVELOPMENT_RAZORPAY_X_WEBHOOK_SECRET")

SEGMENT_KEY = os.getenv("DEVELOPMENT_SEGMENT_KEY")

CRONTAB_DJANGO_SETTINGS_MODULE = 'init.settings.development'

FB_ACCESS_TOKEN = os.getenv("DEVELOPMENT_FB_ACCESS_TOKEN")
FB_PIXEL_ID = os.getenv("DEVELOPMENT_FB_PIXEL_ID")

USE_INTERNAL_FILE_LOGGER = True
OMIT_200_OK_FULL_RESPONSE = False

AWS_CREDENTIALS = {
    'ACCESS_KEY': os.getenv('DEVELOPMENT_AWS_S3_ACCESS_KEY'),
    'SECRET_KEY': os.getenv('DEVELOPMENT_AWS_S3_SECRET_KEY')
}

S3_BUCKETS = {
    'media_bucket': {
        'arn': 'arn:aws:s3:::beta-likeminds-media',
        'name': 'beta-likeminds-media',
        'region': 'ap-south-1'
    }
}
