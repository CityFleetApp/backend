# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from .serializers import (SignupSerializer, ResetPasswordSerializer, ChangePasswordSerializer,
                          UserDetailSerializer, ContactsSerializer)


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


class AddFriendsFromContactsView(APIView):
    '''
    Receive driver's contact numbers, find drivers with these numbers,
    add these drivers to user friends field, return list of user's friends
    '''

    def post(self, request, *args, **kwargs):
        serializer = ContactsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        friends = serializer.validated_data['users']
        request.user.friends.add(*friends)

        user_data = UserDetailSerializer(friends, many=True).data
        return Response(user_data)

add_contacts_friends = AddFriendsFromContactsView.as_view()
