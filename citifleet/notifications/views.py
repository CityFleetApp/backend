from rest_framework import viewsets
from rest_framework import filters
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('unseen',)

    def get_queryset(self):
        return super(NotificationViewSet, self).get_queryset().filter(user=self.request.user)

    @detail_route(methods=['post'], url_path='mark-seen')
    def mark_seen(self, request, pk=None):
        notification = self.get_object()
        notification.unseen = False
        notification.save()
        return Response(status=status.HTTP_200_OK)
