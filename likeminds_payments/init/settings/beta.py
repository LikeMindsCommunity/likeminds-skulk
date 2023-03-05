import os

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
WEB_URL = os.getenv('BETA_WEB_URL')

ALLOWED_HOSTS = [os.getenv("BETA_ALLOWED_HOST_1"), os.getenv("BETA_ALLOWED_HOST_2"), os.getenv("BETA_ALLOWED_HOST_3")]

RAZORPAY_KEY = os.getenv("BETA_RAZORPAY_KEY")
RAZORPAY_SECRET = os.getenv("BETA_RAZORPAY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("BETA_RAZORPAY_WEBHOOK_SECRET")

RAZORPAY_X_KEY = os.getenv("BETA_RAZORPAY_X_KEY")
RAZORPAY_X_SECRET = os.getenv("BETA_RAZORPAY_X_SECRET")
RAZORPAY_X_ACCOUNT_NUMBER = os.getenv("BETA_RAZORPAY_X_ACCOUNT_NUMBER")
RAZORPAY_X_WEBHOOK_SECRET = os.getenv("BETA_RAZORPAY_X_WEBHOOK_SECRET")

SEGMENT_KEY = os.getenv("BETA_SEGMENT_KEY")

CRONTAB_DJANGO_SETTINGS_MODULE = 'init.settings.beta'

FB_ACCESS_TOKEN = os.getenv("BETA_FB_ACCESS_TOKEN")
FB_PIXEL_ID = os.getenv("BETA_FB_PIXEL_ID")

USE_INTERNAL_FILE_LOGGER = False
OMIT_200_OK_FULL_RESPONSE = True

CORALOGIX_LOGGER = {
    'PRIVATE_API_KEY': os.getenv('BETA_CORALOGIX_LOGGER_PRIVATE_API_KEY'),
    'APPLICATION_NAME': 'LM-SUBSCRIPTIONS-BETA',
    'SUBSYSTEM_NAME_API': 'Backend_App_Api',
    'SUBSYSTEM_NAME_APP': 'Backend_App_System'
}

AWS_CREDENTIALS = {
    'ACCESS_KEY': os.getenv('BETA_AWS_S3_ACCESS_KEY'),
    'SECRET_KEY': os.getenv('BETA_AWS_S3_SECRET_KEY')
}

S3_BUCKETS = {
    'media_bucket': {
        'arn': 'arn:aws:s3:::beta-likeminds-media',
        'name': 'beta-likeminds-media',
        'region': 'ap-south-1'
    }
}
