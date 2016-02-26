from factory import DjangoModelFactory

from citifleet.common.test_utils import FuzzyPoint

from .models import Report


class ReportFactory(DjangoModelFactory):
    location = FuzzyPoint()
    report_type = Report.POLICE

    class Meta:
        model = Report