# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .serializers import SignupSerializer


class SignUpView(APIView):
    serializer_class = SignupSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        return Response({'token': token.key}, status=status.HTTP_200_OK)


signup = SignUpView.as_view()
