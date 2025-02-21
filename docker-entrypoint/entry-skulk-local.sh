source /opt/venv/bin/activate
cd ./likeminds_payments
DJANGO_SETTINGS_MODULE=init.settings.development python manage.py makemigrations
DJANGO_SETTINGS_MODULE=init.settings.development python manage.py migrate
DJANGO_SETTINGS_MODULE=init.settings.development gunicorn --bind 0.0.0.0:8080 init.wsgi
