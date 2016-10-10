# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from citifleet.taskapp.celery import app
from citifleet.fcm_notifications.fcm import CustomFCMNotification


@app.task
def send_push_notification_task(api_key, registration_ids, kwargs):
    from citifleet.fcm_notifications.utils import update_fcmdevice_registration_id, remove_fcmdevice_registration_id

    push_service = CustomFCMNotification(api_key=api_key)
    if not isinstance(registration_ids, list):
        registration_ids = [registration_ids, ]

    kwargs['registration_ids'] = registration_ids
    responses = push_service.notify_multiple_devices(**kwargs)
    for response in responses:
        if response['status_code'] != 200:
            print('some error occurred. Status code: %s', response['status_code'])
            return
        if not response['response']['failure'] and not response['response']['canonical_ids']:
            continue

        registration_ids_to_resend = []  # TODO: probably add resend mechanism
        if response['registration_ids']:
            for i, result in enumerate(response['response'].get('results', [])):
                if result.get('registration_id'):
                    update_fcmdevice_registration_id(response['registration_ids'][i], result['registration_id'])
                elif result.get('error'):
                    if result['error'] == 'Unavailable':
                        registration_ids_to_resend.append(response['registration_ids'][i])
                    else:
                        remove_fcmdevice_registration_id(response['registration_ids'][i])
