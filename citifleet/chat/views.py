from django.shortcuts import render
from django.db import transaction
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from .models import Room


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
