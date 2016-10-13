from django.db.models import Max, Case, When, DateTimeField, F, Count

from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters

from .models import UserRoom, Room
from .serializers import MessageSerializer, ChatFriendSerializer, UserRoomSerializer


class UserRoomViewSet(viewsets.ModelViewSet):
    serializer_class = UserRoomSerializer
    pagination_class = LimitOffsetPagination
    page_size = 20
    filter_backends = (filters.SearchFilter,)
    search_fields = ('room__participants__full_name',)

    def get_queryset(self):
        return UserRoom.objects.filter(user=self.request.user)\
                       .annotate(number=Count('room__messages'))\
                       .annotate(updated=Case(
                            When(number=0, then=F('room__created')),
                            default=Max('room__messages__created'),
                            output_field=DateTimeField(),
                       )).order_by('-updated')

    def get_object(self):
        return UserRoom.objects.get(user=self.request.user, room_id=self.kwargs['pk'])


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    pagination_class = LimitOffsetPagination
    page_size = 20

    def get_queryset(self):
        UserRoom.objects.filter(user=self.request.user, room=self.kwargs['room']).update(unseen=0)
        return Room.objects.filter(
            id=self.kwargs['room'],
            participants=self.request.user
        ).distinct().get().messages.order_by('-created')


class FriendsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatFriendSerializer

    def get_queryset(self):
        return self.request.user.friends.all().exclude(pk=self.request.user.pk)
