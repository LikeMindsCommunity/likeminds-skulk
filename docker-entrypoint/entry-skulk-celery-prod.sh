source /opt/venv/bin/activate
cd ./likeminds_payments
DJANGO_SETTINGS_MODULE=init.settings.production celery -A init worker --loglevel=info
