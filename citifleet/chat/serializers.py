# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
from itertools import chain

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from channels import Group

from citifleet.chat.models import Message, Room, UserRoom


class ChatFriendSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'full_name', 'phone', 'avatar_url', 'email', )


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
    name = serializers.CharField(source='room.name', required=False)
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

    def validate_participants(self, attrs):
        if self.context['request'].user in attrs:
            raise serializers.ValidationError(_('User can\'t start chat with himself'))
        return attrs

    def create(self, validated_data):
        request_user = self.context['request'].user
        participants = validated_data['room'].pop('participants', [])

        if len(participants) == 1:
            try:
                room = Room.objects.annotate(participants_count=Count('participants')).filter(
                    participants=request_user
                ).filter(participants=participants[0]).filter(participants_count=2).get()
                return room.userroom_set.get(user=request_user)
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
        participants = validated_data['room'].pop('participants', [])

        if participants:
            message = {'type': 'room_invitation'}
            message.update(UserRoomSerializer(obj).data)
            if message.get('last_message_timestamp'):
                message['last_message_timestamp'] = message['last_message_timestamp'].isoformat()
            json_message = json.dumps(message)

            for participant in participants:
                _, created = UserRoom.objects.get_or_create(room=obj.room, user=participant)
                if created:
                    Group('chat-%s' % participant.id).send({'text': json_message})

        if validated_data.get('room', {}).get('name'):
            obj.room.name = validated_data['room']['name']
            obj.room.save()

        return obj


class UserRoomListSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    last_message_timestamp = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    participants_info = ChatFriendSerializer(many=True, source='room.participants', read_only=True)
    id = serializers.ReadOnlyField(source='room.id')

    class Meta:
        model = UserRoom
        fields = ('id', 'unseen', 'participants_info', 'last_message',
                  'last_message_timestamp', 'name')

    def get_last_message(self, obj):
        last_message = obj.room.messages.order_by('created').last()
        return last_message.text if last_message else None

    def get_last_message_timestamp(self, obj):
        last_message = obj.room.messages.order_by('created').last()
        return last_message.created if last_message else None

    def get_name(self, obj):
        room = obj.room
        request_user = self.context['request'].user
        if room.participants.exclude(pk=request_user.pk).count() == 1:
            return room.participants.exclude(pk=request_user.pk).get().username
        return room.name or 'Group'
