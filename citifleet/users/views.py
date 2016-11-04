# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import FormView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import list_route, detail_route
from rest_framework.generics import (UpdateAPIView, RetrieveAPIView,
                                     RetrieveUpdateAPIView, GenericAPIView)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.views import APIView

from citifleet.common.utils import PUSH_NOTIFICATION_MESSAGE_TYPES
from citifleet.fcm_notifications.utils import send_mass_push_notifications
from citifleet.users import serializers as users_serializers
from citifleet.users.models import Photo, FriendRequest
from citifleet.users.forms import NotificationForm
from citifleet.common.rest_permissions import UserWithoutSiteAccountOnly, AnonymousOnly

User = get_user_model()


class SignUpView(APIView):
    """ POST - signs up new user and returns authorization token """
    serializer_class = users_serializers.SignupSerializer
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(users_serializers.UserLoginSerializer(user).data, status=status.HTTP_200_OK)

signup = SignUpView.as_view()


class ResetPassword(APIView):
    """ POST - resets password and send new password to user's email """
    serializer_class = users_serializers.ResetPasswordSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.reset_password()
        return Response(status=status.HTTP_200_OK)

reset_password = ResetPassword.as_view()


class ChangePassword(APIView):
    """ POST - change password. No password confirm """
    serializer_class = users_serializers.ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.change_password()
        return Response(status=status.HTTP_200_OK)

change_password = ChangePassword.as_view()


class LoginView(ObtainAuthToken):
    """ Login user, return auth token and user info in response """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        Token.objects.get_or_create(user=user)
        return Response(users_serializers.UserLoginSerializer(user).data, status=status.HTTP_200_OK)

login = LoginView.as_view()


class BaseAddFriendsView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)

        friends = serializer.validated_data['users']
        request.user.friends.add(*friends)

        user_data = users_serializers.UserDetailSerializer(friends, many=True).data
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
    serializer_class = users_serializers.ContactsSerializer

add_contacts_friends = AddFriendsFromContactsView.as_view()


class AddFriendsFromFacebookView(BaseAddFriendsView):
    """
    Receive driver's facebook token and retrieve facebook friends.
    Find drivers among facebook friends and add them to driver's friends
    ---
    POST:
        request_serializer: FacebookSerializer
        response_serializer: UserDetailSerializer
    """
    serializer_class = users_serializers.FacebookSerializer

add_facebook_friends = AddFriendsFromFacebookView.as_view()


class AddFriendsFromTwitterView(BaseAddFriendsView):
    """
    Receive driver's twitter token and token secret. Retrieve twitter friends.
    Find drivers among twitter friends and add them to driver's friends
    ---
    POST:
        request_serializer: TwitterSerializer
        response_serializer: UserDetailSerializer
    """
    serializer_class = users_serializers.TwitterSerializer

add_twitter_friends = AddFriendsFromTwitterView.as_view()


class AddFriendsFromInstagramView(BaseAddFriendsView):
    """
    Receive driver's instagram token. Retrieve instagram friends.
    Find drivers among instagram friends and add them to driver's friends
    ---
    POST:
        request_serializer: InstagramSerializer
        response_serializer: UserDetailSerializer
    """
    serializer_class = users_serializers.InstagramSerializer

add_instagram_friends = AddFriendsFromInstagramView.as_view()


class UploadAvatarView(UpdateAPIView):
    """ Update driver avatar """
    serializer_class = users_serializers.AvatarSerializer

    def get_object(self):
        return self.request.user

upload_avatar = UploadAvatarView.as_view()


class UserInfoView(RetrieveAPIView):
    """ Retrieve driver's info for dashboard """
    serializer_class = users_serializers.UserDetailSerializer

    def get_object(self):
        return self.request.user

info = UserInfoView.as_view()


class PhotoModelViewSet(ModelViewSet):
    """ Model viewset for create/delete photos """
    serializer_class = users_serializers.PhotoSerializer
    queryset = Photo.objects.all()

    def get_queryset(self):
        return super(PhotoModelViewSet, self).get_queryset().filter(user=self.request.user)


class SettingsView(RetrieveUpdateAPIView):
    """ APIView for editing user's settings """
    serializer_class = users_serializers.SettingsSerializer

    def get_object(self):
        return self.request.user

settings = SettingsView.as_view()


class ProfileView(RetrieveUpdateAPIView):
    """ APIView for editing profile's info """
    serializer_class = users_serializers.ProfileSerializer

    def get_object(self):
        return self.request.user

profile = ProfileView.as_view()


class FriendView(RetrieveAPIView):
    serializer_class = users_serializers.UserDetailSerializer

    def get_object(self):
        return User.objects.get(id=self.kwargs['id'])

friend = FriendView.as_view()


class FriendPhotoModelViewSet(ModelViewSet):
    """ Model viewset for create/delete photos """
    serializer_class = users_serializers.PhotoSerializer
    queryset = Photo.objects.all()

    def get_queryset(self):
        return super(FriendPhotoModelViewSet, self).get_queryset().filter(user=self.kwargs['id'])


class SendMassPushNotification(FormView):
    form_class = NotificationForm
    template_name = 'users/notification_form.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(SendMassPushNotification, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        notification_data = {
            'notification_type': PUSH_NOTIFICATION_MESSAGE_TYPES.mass_notification,
        }
        send_mass_push_notifications(
            message_title=form.cleaned_data['text'],
            message_body=form.cleaned_data['text'],
            data_message=notification_data,
        )
        messages.add_message(self.request, messages.SUCCESS, 'Push notification sent')
        return HttpResponseRedirect(reverse('admin:users_user_changelist'))


send_mass_push_notification = SendMassPushNotification.as_view()


class CheckUsernameInUseApiView(APIView):
    serializer_class = users_serializers.UsernameInUseSerializer
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.GET)
        serializer.is_valid(raise_exception=True)
        return Response({}, status=status.HTTP_200_OK)

check_username_in_use = CheckUsernameInUseApiView.as_view()


class UpdateUserLocationApiView(GenericAPIView):
    """ Update user's location """
    serializer_class = users_serializers.UpdateUserLocationSerializer

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({}, status=status.HTTP_200_OK)

update_user_location = UpdateUserLocationApiView.as_view()


class FriendsFromContactsListView(APIView):
    http_method_names = ('post', )
    request_serializer_class = users_serializers.FriendsFromContactsSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.request_serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        friends = serializer.get_users(request.user)
        user_data = users_serializers.SimpleUserSerializer(friends, many=True).data
        return Response(user_data)

friends_from_contacts = FriendsFromContactsListView.as_view()


class FriendRequestViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = users_serializers.CreateFriendRequestSerializer
    queryset = FriendRequest.objects.all()

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['incoming', 'outgoing']:
            return users_serializers.FriendRequestSerializer
        return super(FriendRequestViewSet, self).get_serializer_class()

    def get_queryset(self):
        qs = super(FriendRequestViewSet, self).get_queryset()
        if self.action in ['incoming', 'accept', 'decline']:
            return qs.filter(to_user=self.request.user).order_by('-created')
        elif self.action == 'outgoing':
            return qs.filter(from_user=self.request.user).order_by('-created')
        return qs

    @list_route(methods=['get'])
    def incoming(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @list_route(methods=['get'])
    def outgoing(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @detail_route(methods=['post'])
    def accept(self, request, pk=None, *args, **kwargs):
        friend_request = self.get_object()
        self.request.user.friends.add(friend_request.from_user)
        friend_request.from_user.friends.add(friend_request.to_user)
        friend_request.delete()
        return Response(status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def decline(self, request, pk=None, *args, **kwargs):
        friend_request = self.get_object()
        friend_request.delete()
        return Response(status=status.HTTP_200_OK)


class SocialAuthenticateAPIView(GenericViewSet):
    permission_classes = (AnonymousOnly, )
    social_account_type = None

    def get_serializer_class(self):
        if self.social_account_type == 'facebook':
            if self.action == 'register':
                return users_serializers.FacebookSocialAccountCreateSerializer
            return users_serializers.FacebookAuthSerializer
        if self.social_account_type == 'google':
            if self.action == 'register':
                return users_serializers.GoogleSocialAccountCreateSerializer
            return users_serializers.GoogleAuthSeriaizer

    def authenticate(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.authenticate()
        if user:
            if user.pk:
                Token.objects.get_or_create(user=user)
                return Response(users_serializers.UserLoginSerializer(user).data, status=status.HTTP_200_OK)
            return Response(users_serializers.SocialAuthFailedSerializer(user).data, status=status.HTTP_404_NOT_FOUND)
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.create(serializer.validated_data)
        return Response(users_serializers.UserLoginSerializer(user).data, status=status.HTTP_200_OK)


class SetPasswordAPIView(APIView):
    permission_classes = (UserWithoutSiteAccountOnly, )

    def post(self, request, *args, **kwargs):
        serializer = users_serializers.SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.set_password(request.user)
        return Response({}, status=status.HTTP_200_OK)


SOCIAL_ACTIONS = {
    'post': 'authenticate',
    'put': 'register',
}
google_auth_view = SocialAuthenticateAPIView.as_view(social_account_type='google', actions=SOCIAL_ACTIONS)
facebook_auth_view = SocialAuthenticateAPIView.as_view(social_account_type='facebook', actions=SOCIAL_ACTIONS)
password_set = SetPasswordAPIView.as_view()
