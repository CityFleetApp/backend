import json

from channels import Group

from .models import Room
from .serializers import MessageSerializer, RoomSerializer


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
                print(participant.id)
                print(self.user.id)
                Group('chat-%s' % participant.id).send({'text': json_response})

    def _create_room(self):
        '''
        Create room and send notification to invited participants
        '''
        response = {'type': 'room_invitation'}

        serializer = RoomSerializer(self.msg, context={'user': self.user})
        if serializer.is_valid():
            room = serializer.save()
            response['data'] = RoomSerializer(room).data

            participants = room.participants.exclude(id=self.user.id)
            for participant in participants:
                Group('chat-%s' % participant.id).send(response)

    def _fetch_rooms(self):
        '''
        Fetch user's chat rooms
        '''
        response = {'type': 'rooms_list'}

        rooms = Room.objects.filter(participants__in=[self.user])
        response['data'] = RoomSerializer(rooms, many=True).data
        Group('chat-%s' % self.user.id).send(response)

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

        if self.msg.get('method') == 'create_room':
            self._create_room()

        if self.msg.get('method') == 'post_message':
            self._post_message()

        if self.msg.get('method') == 'fetch_rooms':
            self._fetch_rooms()

        if self.msg.get('method') == 'fetch_messages':
            self._fetch_messages()
