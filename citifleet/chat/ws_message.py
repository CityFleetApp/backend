import json

from channels import Group

from citifleet.common.utils import get_full_path

from .models import UserRoom
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
            if message.image:
                response['image'] = get_full_path(message.image.url)
            json_response = json.dumps(response)

            for participant in message.room.participants.all():
                Group('chat-%s' % participant.id).send({'text': json_response})

    def _read_room(self):
        '''
        User reads new channel messages
        '''
        UserRoom.objects.filter(user=self.user, room_id=self.msg['room']).update(unseen=0)

    def on_message(self, msg):
        '''
        Message routing
        '''
        self.user = msg.user
        self.msg = json.loads(msg.content['text'])

        if self.msg.get('method') == 'post_message':
            self._post_message()

        if self.msg.get('method') == 'read_room':
            self._read_room()
