import json
from itertools import chain

from django.contrib.auth import get_user_model
from django.db.models import Count

from rest_framework import serializers
from channels import Group

from .models import Message, Room, UserRoom


class ChatFriendSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'full_name', 'phone', 'avatar_url')


class MessageSerializer(serializers.ModelSerializer):
    author_info = ChatFriendSerializer(source='author', read_only=True)

    class Meta:
        model = Message
        fields = ('text', 'room', 'author', 'created', 'author_info')


class UserRoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    last_message_timestamp = serializers.SerializerMethodField()
    participants_info = ChatFriendSerializer(many=True, source='room.participants', read_only=True)
    participants = serializers.PrimaryKeyRelatedField(source='room.participants',
                                                      queryset=get_user_model().objects.all(),
                                                      write_only=True, many=True)
    name = serializers.CharField(source='room.name')

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

        for participant in participants:
            UserRoom.objects.get_or_create(room=obj.room, user=participant)

        return obj
