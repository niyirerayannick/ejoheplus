from django.urls import path, include
from rest_framework.routers import DefaultRouter
from opportunities.api import JobViewSet, ScholarshipViewSet, InternshipViewSet
from training.api import CourseViewSet
from mentorship.api import MentorViewSet

router = DefaultRouter()
router.register('jobs', JobViewSet, basename='jobs')
router.register('internships', InternshipViewSet, basename='internships')
router.register('scholarships', ScholarshipViewSet, basename='scholarships')
router.register('trainings', CourseViewSet, basename='trainings')
router.register('courses', CourseViewSet, basename='courses')
router.register('mentors', MentorViewSet, basename='mentors')

urlpatterns = [
    path('', include(router.urls)),
]
