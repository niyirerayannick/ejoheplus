from rest_framework import serializers
from django.utils.text import slugify
from accounts.models import User
from .models import MentorProfile


class MentorSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    professional_title = serializers.CharField(required=False, allow_blank=True)
    company = serializers.CharField(required=False, allow_blank=True)
    years_of_experience = serializers.IntegerField(required=False)
    expertise_areas = serializers.ListField(child=serializers.CharField(), required=False)
    availability_hours = serializers.CharField(required=False, allow_blank=True)
    is_mentor_approved = serializers.BooleanField(required=False)
    created_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        profile = getattr(instance, 'mentor_profile', None)
        expertise = []
        if profile and profile.expertise_areas:
            expertise = [item.strip() for item in profile.expertise_areas.split(',') if item.strip()]
        return {
            'id': instance.id,
            'full_name': instance.get_full_name() or instance.username,
            'email': instance.email,
            'phone': instance.phone or '',
            'bio': instance.bio or '',
            'profile_picture': instance.profile_picture.url if instance.profile_picture else '',
            'professional_title': profile.professional_title if profile else '',
            'company': profile.company if profile else '',
            'years_of_experience': profile.years_of_experience if profile else 0,
            'expertise_areas': expertise,
            'availability_hours': profile.availability_hours if profile else '',
            'is_mentor_approved': instance.is_mentor_approved,
            'created_at': instance.created_at,
        }

    def _unique_username(self, base):
        base_slug = slugify(base) or 'mentor'
        username = base_slug
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_slug}{counter}"
            counter += 1
        return username

    def create(self, validated_data):
        expertise = validated_data.pop('expertise_areas', [])
        professional_title = validated_data.pop('professional_title', '')
        company = validated_data.pop('company', '')
        years_of_experience = validated_data.pop('years_of_experience', 0)
        availability_hours = validated_data.pop('availability_hours', '')
        is_mentor_approved = validated_data.pop('is_mentor_approved', False)

        full_name = validated_data.get('full_name', '').strip()
        email = validated_data.get('email', '').strip().lower()
        username_base = email.split('@')[0] if email else full_name
        username = self._unique_username(username_base)

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=full_name.split(' ')[0] if full_name else '',
            last_name=' '.join(full_name.split(' ')[1:]) if full_name else '',
            role='mentor',
        )
        user.phone = validated_data.get('phone', '')
        user.bio = validated_data.get('bio', '')
        user.is_mentor_approved = is_mentor_approved
        user.save()

        MentorProfile.objects.update_or_create(
            mentor=user,
            defaults={
                'professional_title': professional_title,
                'company': company,
                'years_of_experience': years_of_experience or 0,
                'expertise_areas': ', '.join(expertise),
                'availability_hours': availability_hours,
            },
        )
        return user

    def update(self, instance, validated_data):
        expertise = validated_data.pop('expertise_areas', None)
        profile = getattr(instance, 'mentor_profile', None)
        full_name = validated_data.get('full_name', '').strip()

        if full_name:
            parts = full_name.split(' ')
            instance.first_name = parts[0]
            instance.last_name = ' '.join(parts[1:])
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.bio = validated_data.get('bio', instance.bio)
        if 'is_mentor_approved' in validated_data:
            instance.is_mentor_approved = validated_data['is_mentor_approved']
        instance.save()

        if profile:
            profile.professional_title = validated_data.get('professional_title', profile.professional_title)
            profile.company = validated_data.get('company', profile.company)
            profile.years_of_experience = validated_data.get('years_of_experience', profile.years_of_experience)
            profile.availability_hours = validated_data.get('availability_hours', profile.availability_hours)
            if expertise is not None:
                profile.expertise_areas = ', '.join(expertise)
            profile.save()

        return instance
