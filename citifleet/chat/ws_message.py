import json

from channels import Group

from .models import Room
from .serializers import MessageSerializer


class MessageHandler(object):

    def _post_message(self):
        '''
        Create message and send to other group participants
        '''
        response = {'type': 'receive_message'}

        self.msg['author'] = self.user.id
        serializer = MessageSerializer(data=self.msg)

        if serializer.is_valid():
            message = serializer.save()
            response.update(MessageSerializer(message).data)
            json_response = json.dumps(response)

            for participant in message.room.participants.all():
                Group('chat-%s' % participant.id).send({'text': json_response})

    def _fetch_messages(self):
        '''
        Fetch room's message by room id
        '''
        response = {'type': 'messages'}

        try:
            messages = Room.objects.get(participants__in=[self.user], label=self.msg['label'])
        except Room.DoesNotExist:
            pass
        else:
            response['data'] = MessageSerializer(messages, many=True)
            Group('chat-%s' % self.user.id).send(response)

    def on_message(self, msg):
        '''
        Message routing
        '''
        self.user = msg.user
        self.msg = json.loads(msg.content['text'])

        if self.msg.get('method') == 'post_message':
            self._post_message()
