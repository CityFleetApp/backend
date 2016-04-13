from rest_framework import viewsets

from .models import Room
from .serializers import RoomSerializer, MessageSerializer, ChatFriendSerializer


class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer

    def get_queryset(self):
        return Room.objects.filter(participants__in=[self.request.user])


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer


class FriendsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatFriendSerializer

    def get_queryset(self):
        return self.request.user.friends.all()
