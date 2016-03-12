from rest_framework import viewsets
from rest_framework import filters

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('unseen',)

    def get_queryset(self):
        return super(NotificationViewSet, self).get_queryset().filter(user=self.request.user)
