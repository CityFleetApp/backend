# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from citifleet.taskapp.celery import app
from citifleet.fcm_notifications.fcm import CustomFCMNotification


@app.task
def send_push_notification_task(api_key, registration_ids, kwargs):
    push_service = CustomFCMNotification(api_key=api_key)
    # kwargs['dry_run'] = True
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

    responses = push_method(**kwargs)
    for response in responses:
        if response['status_code'] != 200:
            print('some error occurred. Status code: %s', response['status_code'])
            return
        # TODO: parse response here
