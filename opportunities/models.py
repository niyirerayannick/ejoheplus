from django.db import models
from accounts.models import User


class Opportunity(models.Model):
    TYPE_CHOICES = [
        ('scholarship', 'Scholarship'),
        ('internship', 'Internship'),
        ('job', 'Job'),
        ('volunteer', 'Volunteer'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    requirements = models.TextField()
    benefits = models.TextField(blank=True)
    deadline = models.DateField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='opportunities_created',
        limit_choices_to={'role__in': ['mentor', 'partner']},
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Opportunities'
    
    def __str__(self):
        return self.title


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications', limit_choices_to={'role': 'student'})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='applications/resumes/', blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['opportunity', 'student']
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.opportunity.title}"
