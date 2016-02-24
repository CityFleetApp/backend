from django.conf import settings
from django.contrib.gis.measure import D

from rest_framework import viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from .models import Report
from .serializers import ReportSerializer


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    queryset = Report.objects.all()

    def get_queryset(self):
        return super(ReportViewSet, self).get_queryset().filter(
            location__distance_lte=(self.request.user.location, D(settings.VISIBLE_REPORTS_RADIUS)))

    @detail_route(methods=['post'])
    def confirm_report(self, request, pk=None):
        report = self.get_object()
        report.save()
        return Response(status.HTTP_200_OK)
