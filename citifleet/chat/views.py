from django.db.models import Max, Case, When, DateTimeField, F, Count

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Room, Message
from .serializers import RoomSerializer, MessageSerializer, ChatFriendSerializer


class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    pagination_class = PageNumberPagination
    page_size = 10

    def get_queryset(self):
        return Room.objects.filter(participants=self.request.user)\
            .annotate(number=Count('messages'))\
            .annotate(updated=Case(
                When(number=0, then=F('created')),
                default=Max('messages__created'),
                output_field=DateTimeField(),
            )).order_by('-updated')


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(room=self.kwargs['room'], room__participants=self.request.user)


class FriendsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatFriendSerializer

    def get_queryset(self):
        return self.request.user.friends.all()
