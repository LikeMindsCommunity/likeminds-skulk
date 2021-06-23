from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

TIME_ZONE = 'Asia/Kolkata'

# variable to check for beta server
IS_BETA = True

URL = os.getenv("DEVELOPMENT_URL")
CORE_SERVICE_URL = os.getenv("DEVELOPMENT_CORE_URL")

ALLOWED_HOSTS = [os.getenv("DEVELOPMENT_ALLOWED_HOST_1"), os.getenv("DEVELOPMENT_ALLOWED_HOST_2")]

RAZORPAY_KEY = os.getenv("RAZORPAY_KEY")
RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

SEGMENT_KEY = os.getenv('SEGMENT_KEY')
