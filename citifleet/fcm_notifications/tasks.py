# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from citifleet.taskapp.celery import app
from citifleet.fcm_notifications.fcm import CustomFCMNotification


@app.task
def send_push_notification_task(api_key, registration_ids, kwargs):
    from citifleet.fcm_notifications.utils import update_fcmdevice_registration_id, remove_fcmdevice_registration_id

    logger = send_push_notification_task.get_logger()

    push_service = CustomFCMNotification(api_key=api_key)
    if not isinstance(registration_ids, list):
        registration_ids = [registration_ids, ]

    logger.debug('Send push notification to %s registration ids with kwargs: %s', len(registration_ids), kwargs)

    kwargs['registration_ids'] = registration_ids
    responses = push_service.notify_multiple_devices(**kwargs)
    logger.debug('Receive %s responses', len(responses))

    for response in responses:
        if response['status_code'] != 200:
            logger.debug('Some error occurred. Status code: %s', response['status_code'])
            return

        if not response['response']['failure'] and not response['response']['canonical_ids']:
            logger.debug('There are nothing to process. Successful response.')
            continue

        registration_ids_to_resend = []
        if response['registration_ids']:
            for i, result in enumerate(response['response'].get('results', [])):
                if result.get('registration_id'):
                    logger.debug(
                        'Update registration id from %s to %s',
                        response['registration_ids'][i],
                        result['registration_id']
                    )
                    update_fcmdevice_registration_id(response['registration_ids'][i], result['registration_id'])
                elif result.get('error'):
                    if result['error'] == 'Unavailable':
                        registration_ids_to_resend.append(response['registration_ids'][i])
                    else:
                        logger.debug('Remove device with registration id %s', response['registration_ids'][i])
                        remove_fcmdevice_registration_id(response['registration_ids'][i])

        logger.debug('Push notifications are successfully sent')
