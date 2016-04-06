import json

from channels import Group
from channels.auth import channel_session_user_from_http, channel_session_user

from .models import Room
from .serializers import MessageSerializer


@channel_session_user_from_http
def ws_connect(message):
    Group('chat-' + message.user.id).add(message.reply_channel)


@channel_session_user
def ws_receive(message):
    data = json.loads(message['text'])

    try:
        room = Room.objects.get(label=data['room'], participants__in=[message.user])
    except Room.DoesNotExist:
        pass
    else:
        chat_message = room.messages.create(text=data['message'], author=message.user)
        serializer = MessageSerializer(chat_message)
        Group('chat-' + message.user.id).send({'text': json.dumps(serializer.data)})


@channel_session_user
def ws_disconnect(message):
    Group('chat-' + message.user.id).discard(message.reply_channel)
