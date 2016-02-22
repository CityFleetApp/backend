from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import User


class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone', 'hack_license', 'password')

    def validate_hack_license(self, value):
        # TODO: check license via SODA
        return value

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return token
