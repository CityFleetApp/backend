from channels import Group
from channels.auth import channel_session_user_from_http, channel_session_user

from .ws_message import MessageHandler


@channel_session_user_from_http
def ws_connect(message):
    Group('chat-%s' % message.user.id).add(message.reply_channel)


@channel_session_user
def ws_receive(message):
    handler = MessageHandler()
    handler.on_message(message)


@channel_session_user
def ws_disconnect(message):
    Group('chat-%s' % message.user.id).discard(message.reply_channel)
