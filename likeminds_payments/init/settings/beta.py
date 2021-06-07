from .base import *

DEBUG = True

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

ALLOWED_HOSTS = [os.getenv("BETA_ALLOWED_HOST_1"), os.getenv("BETA_ALLOWED_HOST_2")]

RAZORPAY_KEY = os.getenv("RAZORPAY_KEY")
RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")
