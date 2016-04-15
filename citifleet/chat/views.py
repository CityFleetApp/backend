from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Room
from .serializers import RoomSerializer, MessageSerializer, ChatFriendSerializer


class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    pagination_class = PageNumberPagination
    page_size = 10

    def get_queryset(self):
        return Room.objects.filter(participants__in=[self.request.user])


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer


class FriendsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatFriendSerializer

    def get_queryset(self):
        return self.request.user.friends.all()
