# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import requests

from pyfcm import FCMNotification


class CustomFCMNotification(FCMNotification):

    def notify_single_device(self,
                             registration_id=None,
                             message_body=None,
                             message_title=None,
                             message_icon=None,
                             sound=None,
                             condition=None,
                             collapse_key=None,
                             delay_while_idle=False,
                             time_to_live=None,
                             restricted_package_name=None,
                             low_priority=False,
                             dry_run=False,
                             data_message=None,
                             click_action=None,
                             badge=None,
                             color=None,
                             tag=None,
                             body_loc_key=None,
                             body_loc_args=None,
                             title_loc_key=None,
                             title_loc_args=None):
        # [registration_id] cos we're sending to a single device
        payload = self.parse_payload(registration_ids=[registration_id],
                                     message_body=message_body,
                                     message_title=message_title,
                                     message_icon=message_icon,
                                     sound=sound,
                                     collapse_key=collapse_key,
                                     delay_while_idle=delay_while_idle,
                                     time_to_live=time_to_live,
                                     restricted_package_name=restricted_package_name,
                                     low_priority=low_priority,
                                     dry_run=dry_run, data_message=data_message, click_action=click_action,
                                     badge=badge,
                                     color=color,
                                     tag=tag,
                                     body_loc_key=body_loc_key,
                                     body_loc_args=body_loc_args,
                                     title_loc_key=title_loc_key,
                                     title_loc_args=title_loc_args)

        return self.send_request([([registration_id], payload), ])

    def notify_multiple_devices(self,
                                registration_ids=None,
                                message_body=None,
                                message_title=None,
                                message_icon=None,
                                sound=None,
                                condition=None,
                                collapse_key=None,
                                delay_while_idle=False,
                                time_to_live=None,
                                restricted_package_name=None,
                                low_priority=False,
                                dry_run=False,
                                data_message=None,
                                click_action=None,
                                badge=None,
                                color=None,
                                tag=None,
                                body_loc_key=None,
                                body_loc_args=None,
                                title_loc_key=None,
                                title_loc_args=None):

        if len(registration_ids) > self.FCM_MAX_RECIPIENTS:
            payloads = list()
            registration_id_chunks = self.registration_id_chunks(registration_ids)
            for registration_ids in registration_id_chunks:
                payloads.append((
                    registration_ids,
                    self.parse_payload(
                        registration_ids=registration_ids,
                        message_body=message_body,
                        message_title=message_title,
                        sound=sound,
                        message_icon=message_icon,
                        collapse_key=collapse_key,
                        delay_while_idle=delay_while_idle,
                        time_to_live=time_to_live,
                        restricted_package_name=restricted_package_name,
                        low_priority=low_priority,
                        dry_run=dry_run, data_message=data_message,
                        click_action=click_action,
                        badge=badge,
                        color=color,
                        tag=tag,
                        body_loc_key=body_loc_key,
                        body_loc_args=body_loc_args,
                        title_loc_key=title_loc_key,
                        title_loc_args=title_loc_args
                    )
                ))
            return self.send_request(payloads)
        else:
            payload = self.parse_payload(registration_ids=registration_ids,
                                         message_body=message_body,
                                         message_title=message_title,
                                         message_icon=message_icon,
                                         sound=sound,
                                         collapse_key=collapse_key,
                                         delay_while_idle=delay_while_idle,
                                         time_to_live=time_to_live,
                                         restricted_package_name=restricted_package_name,
                                         low_priority=low_priority,
                                         dry_run=dry_run, data_message=data_message, click_action=click_action,
                                         badge=badge,
                                         color=color,
                                         tag=tag,
                                         body_loc_key=body_loc_key,
                                         body_loc_args=body_loc_args,
                                         title_loc_key=title_loc_key,
                                         title_loc_args=title_loc_args)
            return self.send_request([(registration_ids, payload), ])

    def notify_topic_subscribers(self,
                                 topic_name=None,
                                 message_body=None,
                                 message_title=None,
                                 message_icon=None,
                                 sound=None,
                                 condition=None,
                                 collapse_key=None,
                                 delay_while_idle=False,
                                 time_to_live=None,
                                 restricted_package_name=None,
                                 low_priority=False,
                                 dry_run=False,
                                 data_message=None,
                                 click_action=None,
                                 badge=None,
                                 color=None,
                                 tag=None,
                                 body_loc_key=None,
                                 body_loc_args=None,
                                 title_loc_key=None,
                                 title_loc_args=None):
        payload = self.parse_payload(topic_name=topic_name,
                                     condition=condition,
                                     message_body=message_body,
                                     message_title=message_title,
                                     message_icon=message_icon,
                                     sound=sound,
                                     collapse_key=collapse_key,
                                     delay_while_idle=delay_while_idle,
                                     time_to_live=time_to_live,
                                     restricted_package_name=restricted_package_name,
                                     low_priority=low_priority,
                                     dry_run=dry_run, data_message=data_message, click_action=click_action,
                                     badge=badge,
                                     color=color,
                                     tag=tag,
                                     body_loc_key=body_loc_key,
                                     body_loc_args=body_loc_args,
                                     title_loc_key=title_loc_key,
                                     title_loc_args=title_loc_args)
        return self.send_request([([], payload), ])

    def send_request(self, payloads=None):
        responses = []
        payloads = payloads or []
        for registration_ids, payload in payloads:
            if self.FCM_REQ_PROXIES:
                response = requests.post(self.FCM_END_POINT, headers=self.request_headers(),
                                         data=payload, proxies=self.FCM_REQ_PROXIES)
            else:
                response = requests.post(self.FCM_END_POINT, headers=self.request_headers(), data=payload)

            response_data = {
                'registration_ids': registration_ids,
                'status_code': response.status_code,
            }
            if response.status_code == 200:
                response_data['response'] = self.parse_response(response)
            responses.append(response_data)

        return responses
