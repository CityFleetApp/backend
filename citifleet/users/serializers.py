from django.core.mail import send_mail
from django.conf import settings

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from open_facebook import OpenFacebook
from instagram.client import InstagramAPI
import tweepy

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


class FacebookSerializer(serializers.Serializer):
    '''
    Take facebook token and facebook id
    Fetch friends list from facebook
    '''
    token = serializers.CharField()

    def validate(self, attrs):
        graph = OpenFacebook(attrs['token'])
        self_id = graph.get('me', fields='id')['id']
        friends_ids = graph.get('me/friends', fields='id')['data']
        attrs['users'] = User.objects.filter(facebook_id__in=[f['id'] for f in friends_ids])

        user = self.context['user']
        if not user.facebook_id:
            user.facebook_id = self_id
            user.save()
        return attrs


class TwitterSerializer(serializers.Serializer):
    '''
    Take twitter token and secret token
    Fetch friends list from twitter
    '''
    token = serializers.CharField()
    token_secret = serializers.CharField()

    def validate(self, attrs):
        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
        auth.set_access_token(attrs['token'], attrs['token_secret'])
        api = tweepy.API(auth)

        me = api.me()
        friends_ids = api.friends_ids(me.id)
        attrs['users'] = User.objects.filter(twitter_id__in=friends_ids)

        user = self.context['user']
        if not user.twitter_id:
            user.twitter_id = me.id
            user.save()
        return attrs


class InstagramSerializer(serializers.Serializer):
    '''
    Take instagram token
    Fetch friends list from instagram
    '''
    token = serializers.CharField()

    def validate(self, attrs):
        api = InstagramAPI(access_token=attrs['token'], client_secret=settings.INSTAGRAM_CLIENT_SECRET)

        me = api.user()
        follows, next_ = api.user_follows()
        while next_:
            more_follows, next_ = api.user_follows(with_next_url=next_)
            follows.extend(more_follows)

        attrs['users'] = User.objects.filter(insagram_id__in=[f['id'] for f in follows])

        user = self.context['user']
        if not user.instagram_id:
            user.instagram_id = me.id
            user.save()
        return attrs
