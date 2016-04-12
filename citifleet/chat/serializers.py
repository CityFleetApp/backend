from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from rest_framework import serializers
from channels import Group

from .models import Message, Room


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ('text', 'room', 'author', 'created')

    def create(self, validated_data):
        message = super(MessageSerializer, self).create(validated_data)
        Group('chat-' + message.author.id).send({'text': message})


class ChatFriendSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'full_name', 'phone', 'avatar_url')


class RoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    last_message_timestamp = serializers.SerializerMethodField()
    participants = ChatFriendSerializer(many=True)

    class Meta:
        model = Room
        fields = ('name', 'label', 'participants', 'last_message', 'last_message_timestamp')
        read_only_fields = ('label',)

    def get_last_message(self, obj):
        return obj.messages.order_by('created').last()

    def get_last_message_timestamp(self, obj):
        return obj.messages.order_by('created').last().created

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

        room.participants.add(self.context['request'].user)
        room.participants.add(*participants)
        return room


