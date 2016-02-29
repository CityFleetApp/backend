from django.core.mail import send_mail
from django.conf import settings

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from citifleet.common.utils import validate_license

from .models import User


class SignupSerializer(serializers.ModelSerializer):
    '''
    Serializes sign up data. Creates new user and logins it automatically
    '''
    password_confirm = serializers.CharField(max_length=128)

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone', 'hack_license', 'username',
                  'password', 'password_confirm')

    def validate(self, attrs):
        '''
        Validates driver's hack license and full name via SODA API
        '''
        if not validate_license(attrs['hack_license'], attrs['full_name']):
            raise serializers.ValidationError('Invalid license number')

        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")

        del attrs['password_confirm']
        return attrs

    def create(self, validated_data):
        '''
        Saves user, creates and returns authentication token to skip login step
        '''
        user = User.objects.create_user(**validated_data)
        token = Token.objects.create(user=user)
        return token


class ResetPasswordSerializer(serializers.Serializer):
    '''
    Serializes email and provides method to reset password for user
    with passed email
    '''
    email = serializers.EmailField()

    def validate(self, attrs):
        '''
        Checks if user with passed email exists in database
        '''
        try:
            self.user = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email address")

        return attrs

    def reset_password(self):
        '''
        Generate and set new password. Send email with new password
        '''
        new_password = User.objects.make_random_password(length=10)
        self.user.set_password(new_password)
        self.user.save()

        send_mail('Password reset', 'Your new password is {}'.format(new_password),
                  settings.DEFAULT_FROM_EMAIL, [self.user.email])


class ChangePasswordSerializer(serializers.Serializer):
    '''
    Serialize new password's length and provide method to change password
    '''
    password = serializers.CharField(max_length=128)

    def change_password(self):
        '''
        Get user from serializer's context and change password
        '''
        user = self.context['user']
        user.set_password(self.validated_data['password'])
        user.save()


class UserDetailSerializer(serializers.ModelSerializer):
    '''
    Serializer for user details screen
    '''

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone', 'hack_license', 'username',
                  'bio', 'drives', 'avatar_url')


class ContactsSerializer(serializers.Serializer):
    '''
    Take list of phone numbers and return list of users with these numbers
    '''
    contacts = serializers.ListField(child=serializers.CharField())

    def validate(self, attrs):
        attrs['users'] = User.objects.filter(phone__in=attrs['contacts'])
        return attrs
