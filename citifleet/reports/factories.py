from factory import DjangoModelFactory, SubFactory

from citifleet.common.test_utils import FuzzyPoint
from citifleet.users.factories import UserFactory

from .models import Report


class ReportFactory(DjangoModelFactory):
    location = FuzzyPoint()
    report_type = Report.POLICE
    user = SubFactory(UserFactory)

    class Meta:
        model = Report
