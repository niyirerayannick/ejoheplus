from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Course
from .serializers import CourseSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all().order_by('-created_at')

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

    def perform_create(self, serializer):
        instructor = self.request.user if self.request.user.role == 'mentor' else None
        serializer.save(created_by=self.request.user, instructor=instructor)
