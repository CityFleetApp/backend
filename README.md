## 1. Copy env.example to config directory with name .env
``cp env.example config/.env``

## 2. Local deployment

* ``vagrant up``
* ``vagrant ssh``
* ``./manage.py createsuperuser``
* ``./manage.py runserver 0.0.0.0:8000``

## 2. Celery workers:
    celery worker -A citifleet.taskapp.celery.app -l info
    celery beat -A citifleet.taskapp.celery.app -l info
