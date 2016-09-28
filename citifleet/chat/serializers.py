import json
from itertools import chain

from django.contrib.auth import get_user_model
from django.db.models import Count

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from channels import Group

from .models import Message, Room, UserRoom


class ChatFriendSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'full_name', 'phone', 'avatar_url')


class MessageSerializer(serializers.ModelSerializer):
    participants = ChatFriendSerializer(source='room.participants', read_only=True, many=True)
    image = Base64ImageField(allow_null=True, allow_empty_file=True)
    image_size = serializers.SerializerMethodField()

    def get_image_size(self, obj):
        if obj.image:
            return [obj.image.width, obj.image.height]
        else:
            return None

    class Meta:
        model = Message
        fields = ('text', 'room', 'author', 'created', 'participants', 'image', 'image_size')


class UserRoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    last_message_timestamp = serializers.SerializerMethodField()
    participants_info = ChatFriendSerializer(many=True, source='room.participants', read_only=True)
    participants = serializers.PrimaryKeyRelatedField(source='room.participants',
                                                      queryset=get_user_model().objects.all(),
                                                      write_only=True, many=True)
    name = serializers.CharField(source='room.name')
    id = serializers.ReadOnlyField(source='room.id')

    class Meta:
        model = UserRoom
        fields = ('id', 'unseen', 'participants', 'participants_info',
                  'last_message', 'last_message_timestamp', 'name')

    def get_last_message(self, obj):
        last_message = obj.room.messages.order_by('created').last()
        return last_message.text if last_message else None

    def get_last_message_timestamp(self, obj):
        last_message = obj.room.messages.order_by('created').last()
        return last_message.created if last_message else None

    def create(self, validated_data):
        participants = validated_data['room'].pop('participants')

        if len(participants) == 1:
            try:
                room = Room.objects.annotate(number=Count('participants'))\
                                   .filter(participants=self.context['request'].user)\
                                   .filter(participants=participants[0])\
                                   .get(number=2)
                return room.userroom_set.get(user=self.context['request'].user)
            except Room.DoesNotExist:
                pass

        room = Room.objects.create(**validated_data['room'])

        user_room = UserRoom.objects.create(room=room, user=self.context['request'].user)
        for participant in participants:
            UserRoom.objects.create(room=room, user=participant)

        message = {'type': 'room_invitation'}
        message.update(UserRoomSerializer(user_room).data)
        json_message = json.dumps(message)

        for participant in chain(participants, [self.context['request'].user]):
            Group('chat-%s' % participant.id).send({'text': json_message})

        return user_room

    def update(self, obj, validated_data):
        participants = validated_data['room'].pop('participants')

        message = {'type': 'room_invitation'}
        message.update(UserRoomSerializer(obj).data)
        if message.get('last_message_timestamp'):
            message['last_message_timestamp'] = message['last_message_timestamp'].isoformat()
        json_message = json.dumps(message)

        for participant in participants:
            _, created = UserRoom.objects.get_or_create(room=obj.room, user=participant)
            if created:
                Group('chat-%s' % participant.id).send({'text': json_message})

        return obj
