from django.conf import settings
from django.contrib.gis.measure import D
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from citifleet.users.serializers import FriendSerializer

from .models import Report
from .serializers import ReportSerializer, LocationSerializer


class BaseReportViewSet(viewsets.ModelViewSet):
    '''
    GET - returns list of nearby reports
    DELETE - removes report
    '''
    serializer_class = ReportSerializer
    queryset = Report.objects.all()

    def list(self, request, *args, **kwargs):
        '''
        Validate location passed in GET request
        '''
        serializer = LocationSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        self.location = serializer.validated_data['location']
        return super(BaseReportViewSet, self).list(request, *args, **kwargs)

    def get_object(self):
        '''
        Return object by passed pk from all reports, not from get_queryset result
        '''
        return get_object_or_404(Report, pk=self.kwargs['pk'])

    def get_queryset(self):
        return super(BaseReportViewSet, self).get_queryset().filter(
            location__distance_lte=(self.location, D(settings.VISIBLE_REPORTS_RADIUS)))

    @detail_route(methods=['post'])
    def confirm_report(self, request, pk=None):
        '''
        Updates report's last updated date so that it still appears on the map
        '''
        report = self.get_object()
        report.save()
        return Response(status.HTTP_200_OK)


class NearbyReportViewSet(BaseReportViewSet):

    def list(self, request, *args, **kwargs):
        '''
        Save current user location on GET request
        '''
        resp = super(NearbyReportViewSet, self).list(request, *args, **kwargs)
        self.request.user.location = self.location
        self.request.user.save()
        return resp


class MapReportViewSet(BaseReportViewSet):
    pass


class FriendViewSet(BaseReportViewSet):
    serializer_class = FriendSerializer

    def get_queryset(self):
        return self.request.user.friends.filter(
            location__distance_lte=(self.location, D(m=settings.VISIBLE_REPORTS_RADIUS)),
            visible=True)
