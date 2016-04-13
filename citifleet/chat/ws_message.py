import json

from channels import Group

from .serializers import MessageSerializer, RoomSerializer


class MessageHandler(object):

    def _post_message(self):
        '''
        Create message and send to other group participants
        '''
        response = {'type': 'message_posted'}

        self.msg['author'] = self.user
        serializer = MessageSerializer(data=self.msg)

        if serializer.is_valid():
            message = serializer.save()
            response['data'] = MessageSerializer(message).data

            participants = message.room.participants.exclude(id=self.user.id)
            for participant in participants:
                Group('chat-' + participant.id).send(response)

    def _create_room(self):
        '''
        Create room and send notification to invited participants
        '''
        response = {'type': 'room_created'}

        serializer = RoomSerializer(self.msg, context={'user': self.user})
        if serializer.is_valid():
            room = serializer.save()
            response['data'] = RoomSerializer(room).data

            participants = room.participants.exclude(id=self.user.id)
            for participant in participants:
                Group('chat-' + participant.id).send(response)

    def on_message(self, msg):
        '''
        Message routing
        '''
        self.user = msg.user
        self.msg = json.loads(msg)

        if msg.get('method') == 'create_room':
            self._create_room()

        if msg.get('method') == 'post_message':
            self._post_message()

        if msg.get('method') == 'fetch_rooms':
            self._fetch_rooms()

        if msg.get('method') == 'fetch_messages':
            self._fetch_messages()
