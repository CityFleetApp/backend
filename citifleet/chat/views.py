from django.db.models import Max, Case, When, DateTimeField, F, Count

from rest_framework import viewsets

from .models import UserRoom
from .serializers import MessageSerializer, ChatFriendSerializer, UserRoomSerializer


class UserRoomViewSet(viewsets.ModelViewSet):
    serializer_class = UserRoomSerializer

    def get_queryset(self):
        return UserRoom.objects.filter(user=self.request.user)\
                       .annotate(number=Count('room__messages'))\
                       .annotate(updated=Case(
                            When(number=0, then=F('room__created')),
                            default=Max('room__messages__created'),
                            output_field=DateTimeField(),
                       )).order_by('-updated')


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer

    def get_queryset(self):
        UserRoom.objects.filter(user=self.request.user, id=self.kwargs['room']).update(unseen=0)
        return UserRoom.objects.get(id=self.kwargs['room'], user=self.request.user).room.messages.all()


class FriendsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatFriendSerializer

    def get_queryset(self):
        return self.request.user.friends.all()
