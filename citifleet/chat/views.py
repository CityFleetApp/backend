from django.shortcuts import render
from django.db import transaction
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from rest_framework import viewsets

from .models import Room
from .serializers import RoomSerializer, MessageSerializer, ChatFriendSerializer


def chat_room(request, label):
    """
    Room view - show the room, with latest messages.
    The template for this view has the WebSocket business to send and stream
    messages, so see the template for where the magic happens.
    """
    # If the room with the given label doesn't exist, automatically create it
    # upon first visit (a la etherpad).
    room, created = Room.objects.get_or_create(label=label)

    # We want to show the last 50 messages, ordered most-recent-last
    messages = reversed(room.messages.all()[:50])

    return render(request, "chat.html", {
        'room': room,
        'messages': messages,
    })


def new_room(request):
    """
    Randomly create a new room, and redirect to it.
    """
    new_room = None
    label = 1
    while not new_room:
        with transaction.atomic():
            if Room.objects.filter(label=label).exists():
                label += 1
                continue
            new_room = Room.objects.create(label=label)
    return HttpResponseRedirect(reverse('chat:chat_room', kwargs={'label': label}))


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
