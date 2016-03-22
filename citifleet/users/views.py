# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from rest_framework.generics import UpdateAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from push_notifications.models import GCMDevice, APNSDevice

from .serializers import (SignupSerializer, ResetPasswordSerializer, ChangePasswordSerializer,
                          UserDetailSerializer, ContactsSerializer, FacebookSerializer, TwitterSerializer,
                          InstagramSerializer, PhotoSerializer, AvatarSerializer, SettingsSerializer)
from .models import Photo


class SignUpView(APIView):
    '''
    POST - signs up new user and returns authorization token
    '''
    serializer_class = SignupSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        return Response({'token': token.key}, status=status.HTTP_200_OK)


signup = SignUpView.as_view()


class ResetPassword(APIView):
    '''
    POST - resets password and send new password to user's email
    '''
    serializer_class = ResetPasswordSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.reset_password()
        return Response(status=status.HTTP_200_OK)

reset_password = ResetPassword.as_view()


class ChangePassword(APIView):
    '''
    POST - change password. No password confirm
    '''
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.change_password()
        return Response(status=status.HTTP_200_OK)

change_password = ChangePassword.as_view()


class LoginView(ObtainAuthToken):
    '''
    Custom login API.
    Login user, return auth token and user info in response
    '''

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        user_data = UserDetailSerializer(user).data
        user_data['token'] = token.key

        return Response(user_data)

login = LoginView.as_view()


class BaseAddFriendsView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)

        friends = serializer.validated_data['users']
        request.user.friends.add(*friends)

        user_data = UserDetailSerializer(friends, many=True).data
        return Response(user_data)


class AddFriendsFromContactsView(BaseAddFriendsView):
    """
    Receive driver's contact numbers, find drivers with these numbers,
    add these drivers to user friends field, return list of user's friends
    ---
    POST:
        parameters:
            - name: contacts
              description: List of phone numbers
              required: true
              type: array
              paramType: form
        response_serializer: UserDetailSerializer
    """
    serializer_class = ContactsSerializer

add_contacts_friends = AddFriendsFromContactsView.as_view()


class AddFriendsFromFacebookView(BaseAddFriendsView):
    '''
    Receive driver's facebook token and retrieve facebook friends.
    Find drivers among facebook friends and add them to driver's friends
    ---
    POST:
        request_serializer: FacebookSerializer
        response_serializer: UserDetailSerializer
    '''
    serializer_class = FacebookSerializer

add_facebook_friends = AddFriendsFromFacebookView.as_view()


class AddFriendsFromTwitterView(BaseAddFriendsView):
    '''
    Receive driver's twitter token and token secret. Retrieve twitter friends.
    Find drivers among twitter friends and add them to driver's friends
    ---
    POST:
        request_serializer: TwitterSerializer
        response_serializer: UserDetailSerializer
    '''
    serializer_class = TwitterSerializer

add_twitter_friends = AddFriendsFromTwitterView.as_view()


class AddFriendsFromInstagramView(BaseAddFriendsView):
    '''
    Receive driver's instagram token. Retrieve instagram friends.
    Find drivers among instagram friends and add them to driver's friends
    ---
    POST:
        request_serializer: InstagramSerializer
        response_serializer: UserDetailSerializer
    '''
    serializer_class = InstagramSerializer

add_instagram_friends = AddFriendsFromInstagramView.as_view()


class UploadAvatarView(UpdateAPIView):
    '''
    Update driver avatar
    '''
    serializer_class = AvatarSerializer

    def get_object(self):
        return self.request.user

upload_avatar = UploadAvatarView.as_view()


class UserInfoView(RetrieveAPIView):
    '''
    Retrieve driver's info for dashboard
    '''
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user

info = UserInfoView.as_view()


class PhotoModelViewSet(ModelViewSet):
    '''
    Model viewset for create/delete photos
    '''
    serializer_class = PhotoSerializer
    queryset = Photo.objects.all()

    def get_queryset(self):
        return super(PhotoModelViewSet, self).get_queryset().filter(user=self.request.user)


class SettingsView(RetrieveUpdateAPIView):
    serializer_class = SettingsSerializer

    def get_object(self):
        return self.request.user

settings = SettingsView.as_view()
