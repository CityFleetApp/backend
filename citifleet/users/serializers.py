from rest_framework import serializers
from rest_framework.authtoken.models import Token

from citifleet.common.utils import validate_license

from .models import User


class SignupSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone', 'hack_license', 'username',
                  'password', 'password_confirm')

    def validate(self, attrs):
        if not validate_license(attrs['hack_license'], attrs['full_name']):
            raise serializers.ValidationError('Invalid license number')

        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")

        del attrs['password_confirm']
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        token = Token.objects.create(user=user)
        return token
