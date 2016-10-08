# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyfcm import FCMNotification

from citifleet.taskapp.celery import app


@app.task
def send_push_notification_task(api_key, registration_ids, kwargs):
    push_service = FCMNotification(api_key=api_key)
    if not isinstance(registration_ids, list):
        registration_ids = [registration_ids, ]

    if len(registration_ids) == 1:
        kwargs.update({
            'registration_id': registration_ids[0],
        })
        push_method = push_service.notify_single_device
    else:
        kwargs.update({
            'registration_ids': registration_ids
        })
        push_method = push_service.notify_multiple_devices

    resp = push_method(**kwargs)
    print(resp)
