from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('title', 'message', 'created', 'unseen', 'id')
        model = Notification
