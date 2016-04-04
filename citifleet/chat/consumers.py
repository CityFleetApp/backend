import json

from channels import Group
from channels.auth import channel_session_user_from_http, channel_session_user

from .models import Room
from .serializers import MessageSerializer


@channel_session_user_from_http
def ws_connect(message):
    prefix, label = message['path'].strip('/').split('/')
    room = Room.objects.get(label=label)
    Group('chat-' + label).add(message.reply_channel)
    message.channel_session['room'] = room.label


@channel_session_user
def ws_receive(message):
    label = message.channel_session['room']
    room = Room.objects.get(label=label)
    data = json.loads(message['text'])
    message = room.messages.create(text=data['message'], author=message.user)
    serializer = MessageSerializer(message)
    Group('chat-'+label).send({'text': json.dumps(serializer.data)})


@channel_session_user
def ws_disconnect(message):
    label = message.channel_session['room']
    Group('chat-'+label).discard(message.reply_channel)
