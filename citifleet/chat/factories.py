import factory
from factory import DjangoModelFactory

from .models import Room, Message, UserRoom


class RoomFactory(DjangoModelFactory):

    class Meta:
        model = Room

    @factory.post_generation
    def participants(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for participant in extracted:
                UserRoom.objects.create(room=self, user=participant)


class MessageFactory(DjangoModelFactory):

    class Meta:
        model = Message
