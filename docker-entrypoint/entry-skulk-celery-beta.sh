source /opt/venv/bin/activate
cd ./likeminds_payments
DJANGO_SETTINGS_MODULE=init.settings.beta celery -A init worker --loglevel=info -f /usr/src/app/likeminds_payments/logs/celery.log