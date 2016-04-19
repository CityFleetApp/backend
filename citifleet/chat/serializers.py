import json

from django.contrib.auth import get_user_model
from django.db.models import Count

from rest_framework import serializers
from channels import Group

from .models import Message, Room


class ChatFriendSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'full_name', 'phone', 'avatar_url')


class MessageSerializer(serializers.ModelSerializer):
    author_info = ChatFriendSerializer(source='author', read_only=True)

    class Meta:
        model = Message
        fields = ('text', 'room', 'author', 'created', 'author_info')


class RoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    last_message_timestamp = serializers.SerializerMethodField()
    participants_info = ChatFriendSerializer(many=True, source='participants', read_only=True)

    class Meta:
        model = Room
        fields = ('id', 'name', 'participants', 'participants_info', 'last_message', 'last_message_timestamp')

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('created').last()
        return last_message.text if last_message else None

    def get_last_message_timestamp(self, obj):
        last_message = obj.messages.order_by('created').last()
        return last_message.created if last_message else None

    def create(self, validated_data):
        participants = validated_data.pop('participants')

        if len(participants) == 1:
            try:
                room = Room.objects.annotate(number=Count('participants'))\
                                   .filter(participants=self.context['request'].user)\
                                   .filter(participants=participants[0])\
                                   .get(number=2)
                return room
            except Room.DoesNotExist:
                pass

        room = Room(**validated_data)
        room.save()

        room.participants.add(self.context['request'].user)
        room.participants.add(*participants)

        message = {'type': 'room_invitation'}
        message.update(RoomSerializer(room).data)
        json_message = json.dumps(message)

        for participant in participants:
            Group('chat-%s' % participant.id).send({'text': json_message})

        return room
