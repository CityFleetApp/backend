from django.utils import timezone

import factory
from factory import DjangoModelFactory

from .models import Document


class DocumentFactory(DjangoModelFactory):
    file = factory.django.FileField()
    document_type = Document.DMV_LICENSE
    expiry_date = timezone.now()

    class Meta:
        model = Document
