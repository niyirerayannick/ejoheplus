from rest_framework import serializers
from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'slug',
            'category',
            'description',
            'overview',
            'instructor',
            'instructor_name',
            'duration_hours',
            'level',
            'price',
            'is_free',
            'thumbnail',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
