from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.models import User
from .serializers import MentorSerializer


class MentorViewSet(viewsets.ModelViewSet):
    serializer_class = MentorSerializer
    queryset = User.objects.filter(role='mentor').select_related('mentor_profile').order_by('-created_at')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        limit = self.request.query_params.get('limit')
        if limit:
            try:
                limit_val = max(1, min(int(limit), 100))
                queryset = queryset[:limit_val]
            except ValueError:
                pass
        return queryset
