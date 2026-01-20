from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Opportunity
from .serializers import OpportunitySerializer


class BaseOpportunityViewSet(viewsets.ModelViewSet):
    serializer_class = OpportunitySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Opportunity.objects.all().order_by('-created_at')
        limit = self.request.query_params.get('limit')
        if limit:
            try:
                limit_val = max(1, min(int(limit), 100))
                queryset = queryset[:limit_val]
            except ValueError:
                pass
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class JobViewSet(BaseOpportunityViewSet):
    def get_queryset(self):
        return super().get_queryset().filter(type='job')

    def perform_create(self, serializer):
        serializer.save(type='job', created_by=self.request.user)


class ScholarshipViewSet(BaseOpportunityViewSet):
    def get_queryset(self):
        return super().get_queryset().filter(type='scholarship')

    def perform_create(self, serializer):
        serializer.save(type='scholarship', created_by=self.request.user)


class InternshipViewSet(BaseOpportunityViewSet):
    def get_queryset(self):
        return super().get_queryset().filter(type='internship')

    def perform_create(self, serializer):
        serializer.save(type='internship', created_by=self.request.user)
