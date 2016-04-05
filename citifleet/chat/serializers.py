from django.utils.crypto import get_random_string
from rest_framework import serializers

from .models import Message, Room


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ('text', 'room', 'author')


class RoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = ('name', 'label', 'participants')
        read_only_fields = ('label',)

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
