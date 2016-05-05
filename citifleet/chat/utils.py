import functools

from django.contrib.auth.models import AnonymousUser

from channels.handler import AsgiRequest
from rest_framework.authtoken.models import Token

from channels.sessions import channel_session


def token_user(func):
    @functools.wraps(func)
    def inner(message, *args, **kwargs):
        try:
            # We want to parse the WebSocket (or similar HTTP-lite) message
            # to get cookies and GET, but we need to add in a few things that
            # might not have been there.
            if "method" not in message.content:
                message.content['method'] = "FAKE"
            request = AsgiRequest(message)
        except Exception as e:
            raise ValueError("Cannot parse HTTP message - are you sure this is a HTTP consumer? %s" % e)

        token = request.GET.get("token")

        if token:
            try:
                user = Token.objects.get(key=token).user
            except Token.DoesNotExist:
                user = None
        else:
            user = None

        message.user = user
        message.token = token

        result = func(message, *args, **kwargs)
        return result
    return inner


def channel_session_user_from_token(func):
    """
    Decorator that automatically transfers the user from HTTP sessions to
    channel-based sessions, and returns the user as message.user as well.
    Useful for things that consume e.g. websocket.connect
    """
    @token_user
    @channel_session
    def inner(message, *args, **kwargs):
        if message.user is not None:
            message.channel_session['token'] = message.token
        return func(message, *args, **kwargs)
    return inner


def channel_token_user(func):
    """
    Presents a message.user attribute obtained from a user ID in the channel
    session, rather than in the http_session. Turns on channel session implicitly.
    """
    @channel_session
    @functools.wraps(func)
    def inner(message, *args, **kwargs):
        if not hasattr(message, "channel_session"):
            raise ValueError("Did not see a channel session to get auth from")
        if message.channel_session is None:
            message.user = AnonymousUser()
        else:
            message.user = Token.objects.get(key=message.channel_session['token']).user
        # Run the consumer
        return func(message, *args, **kwargs)
    return inner
