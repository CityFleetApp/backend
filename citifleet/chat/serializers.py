from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from rest_framework import serializers

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
        fields = ('id', 'name', 'label', 'participants', 'participants_info', 'last_message', 'last_message_timestamp')
        read_only_fields = ('label',)

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('created').last()
        return last_message.text if last_message else None

    def get_last_message_timestamp(self, obj):
        last_message = obj.messages.order_by('created').last()
        return last_message.created if last_message else None

    def create(self, validated_data):
        participants = validated_data.pop('participants')

        room = None
        while not room:
            label = get_random_string(length=32)
            if Room.objects.filter(label=label).exists():
                continue

            room = Room(**validated_data)
            room.label = label
            room.save()

        room.participants.add(self.context['user'])
        room.participants.add(*participants)
        return room
