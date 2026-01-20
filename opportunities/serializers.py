from rest_framework import serializers
from .models import Opportunity


class OpportunitySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            'id',
            'title',
            'slug',
            'type',
            'category',
            'description',
            'requirements',
            'benefits',
            'deadline',
            'created_by',
            'created_by_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
