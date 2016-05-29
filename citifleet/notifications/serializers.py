from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('title', 'message', 'created', 'unseen', 'id', 'ref_type', 'ref_id')
        model = Notification
