# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .serializers import SignupSerializer, ResetPasswordSerializer, ChangePasswordSerializer


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
