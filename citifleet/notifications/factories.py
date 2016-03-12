from factory import DjangoModelFactory

from .models import Notification


class NotificationFactory(DjangoModelFactory):

    class Meta:
        model = Notification
