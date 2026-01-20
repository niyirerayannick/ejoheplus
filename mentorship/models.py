from django.db import models
from accounts.models import User
from django.utils import timezone
from careers.models import Career, CareerCategory


class MentorshipConnection(models.Model):
    """Connection between a mentor and mentee"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('ended', 'Ended'),
    ]
    
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor_connections', limit_choices_to={'role': 'mentor'})
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentee_connections', limit_choices_to={'role': 'student'})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['mentor', 'mentee']
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.mentor.username} - {self.mentee.username} ({self.status})"


class MentorshipSession(models.Model):
    """Sessions between mentor and mentee"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    connection = models.ForeignKey(MentorshipConnection, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scheduled_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    meeting_link = models.URLField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True, help_text="Session notes and outcomes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"{self.connection.mentor.username} - {self.connection.mentee.username}: {self.title}"
    
    @property
    def is_past(self):
        return self.scheduled_date < timezone.now()


class MentorResource(models.Model):
    """Resources uploaded by mentors"""
    RESOURCE_TYPES = [
        ('document', 'Document'),
        ('video', 'Video'),
        ('link', 'External Link'),
        ('template', 'Template'),
        ('guide', 'Guide'),
        ('other', 'Other'),
    ]
    
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor_resources', limit_choices_to={'role': 'mentor'})
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='document')
    file = models.FileField(upload_to='mentor_resources/', blank=True, null=True)
    external_url = models.URLField(blank=True)
    is_public = models.BooleanField(default=False, help_text="Make this resource available to all mentees")
    connections = models.ManyToManyField(MentorshipConnection, blank=True, related_name='resources', help_text="Specific mentee connections that can access this")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.mentor.username}: {self.title}"


class MentorProfile(models.Model):
    """Extended professional profile for mentors"""
    mentor = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile', limit_choices_to={'role': 'mentor'})
    professional_title = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    years_of_experience = models.IntegerField(default=0)
    expertise_areas = models.TextField(help_text="Comma-separated list of expertise areas")
    education = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    availability_hours = models.CharField(max_length=200, blank=True, help_text="e.g., 'Monday-Friday, 9 AM - 5 PM'")
    max_mentees = models.IntegerField(default=10)
    current_mentee_count = models.IntegerField(default=0)
    career_categories = models.ManyToManyField(CareerCategory, blank=True, related_name='mentors')
    career_focuses = models.ManyToManyField(Career, blank=True, related_name='mentors')
    student_levels = models.CharField(max_length=50, blank=True, help_text="Comma-separated: O-Level, A-Level")
    linkedin_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.mentor.username} - Mentor Profile"
