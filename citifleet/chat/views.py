# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Max, Case, When, DateTimeField, F, Count

from rest_framework import filters, viewsets, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from citifleet.chat.models import UserRoom, Room
from citifleet.chat import serializers as chat_serializers


class UserRoomViewSet(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    page_size = 20
    filter_backends = (filters.SearchFilter, )
    search_fields = ('room__participants__full_name', )
    lookup_field = 'room_id'

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list', ]:
            return chat_serializers.UserRoomListSerializer
        return chat_serializers.UserRoomSerializer

    def get_response_serializer(self, obj):
        return chat_serializers.UserRoomListSerializer(instance=obj, context=self.get_serializer_context())

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            self.get_response_serializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            self.get_response_serializer(serializer.instance).data,
            status=status.HTTP_200_OK
        )

    def get_queryset(self):
        return UserRoom.objects.filter(
            user=self.request.user
        ).annotate(number=Count('room__messages')).annotate(
            updated=Case(
                When(number=0, then=F('room__created')),
                default=Max('room__messages__created'),
                output_field=DateTimeField(),
            )
        ).order_by('-updated').select_related('room', )


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = chat_serializers.MessageSerializer
    pagination_class = LimitOffsetPagination
    page_size = 20

    def get_queryset(self):
        UserRoom.objects.filter(user=self.request.user, room=self.kwargs['room']).update(unseen=0)
        return Room.objects.filter(
            id=self.kwargs['room'],
            participants=self.request.user
        ).distinct().get().messages.order_by('-created')


class FriendsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = chat_serializers.ChatFriendSerializer

    def get_queryset(self):
        return self.request.user.friends.all().exclude(pk=self.request.user.pk)
