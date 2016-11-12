# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from celery.task import periodic_task
from celery.schedules import crontab

from django.utils import timezone as tz
from django.utils.translation import ugettext as _

from citifleet.common.utils import PUSH_NOTIFICATION_MESSAGE_TYPES
from citifleet.documents.models import Document
from citifleet.fcm_notifications.utils import send_push_notifications
from citifleet.users.tasks import send_email_task


@periodic_task(run_every=(crontab(hour='0', minute='0')))
def document_expired_notifications():
    """ Send notification about 30 days, 2 weeks and 5 days before document expiration """

    def get_expired_documents(expire_date):
        return Document.objects.filter(expiry_date=expire_date.date()).select_related('user')

    def match_documents_to_types(docs_qs):
        documents_to_types = {}
        for doc in docs_qs:
            documents_to_type = {'type_repr': doc.get_type_repr()}
            current_docs = documents_to_types.get(
                doc.document_type,
                documents_to_type,
            ).get('docs', [])
            current_docs.append(doc)
            documents_to_type.update({'docs': current_docs})
            documents_to_types[doc.document_type] = documents_to_type

        return documents_to_types

    def notify_about_document_expire(expiry_date, msg_pattern):
        """ Send push and email notifications to users about document expire """
        docs = get_expired_documents(expiry_date)
        match_to_types = match_documents_to_types(docs)
        notification_data = {
            'notification_type': PUSH_NOTIFICATION_MESSAGE_TYPES.document_expire,
        }
        for documents_data in match_to_types.values():
            message = msg_pattern % documents_data['type_repr']
            users = [d.user for d in documents_data['docs']]
            send_push_notifications(
                users,
                message_title=message,
                message_body=message,
                data_message=notification_data,
                sound='default',
                click_action=PUSH_NOTIFICATION_MESSAGE_TYPES.document_expire,
            )

            recipients_emails = [d.user.email for d in documents_data['docs']]
            send_email_task.delay(_('Document expire notification'), message, recipients_emails, )

    now_date = tz.now()
    expire_in_30_days_date = now_date + tz.timedelta(days=30)
    expire_in_14_days_date = now_date + tz.timedelta(days=14)
    expire_in_5_days_date = now_date + tz.timedelta(days=5)
    expired_yesterday_date = now_date - tz.timedelta(days=1)

    notify_about_document_expire(expire_in_30_days_date, _('Document \'%s\' will expire in 30 days'))
    notify_about_document_expire(expire_in_14_days_date, _('Document \'%s\' will expire in 2 weeks'))
    notify_about_document_expire(expire_in_5_days_date, _('Document \'%s\' will expire in 5 days'))
    notify_about_document_expire(expired_yesterday_date, _('Document \'%s\' has been expired'))
