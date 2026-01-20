from django.db import models
from accounts.models import User


class StudentCV(models.Model):
    """Student CV/Resume Builder"""
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cv', limit_choices_to={'role': 'student'})
    
    # Personal Information
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    summary = models.TextField(blank=True, help_text="Professional summary/objective")
    
    # Experience
    experience_json = models.JSONField(default=list, blank=True, help_text="List of work experiences")
    
    # Education
    education_json = models.JSONField(default=list, blank=True, help_text="List of education history")
    
    # Skills
    skills = models.TextField(blank=True, help_text="Comma-separated list of skills")
    
    # Certifications
    certifications_json = models.JSONField(default=list, blank=True, help_text="List of certifications")
    
    # Languages
    languages = models.TextField(blank=True, help_text="Languages spoken")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"CV for {self.student.username}"


class Message(models.Model):
    """Messages between users"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    attachment = models.FileField(upload_to='message_attachments/%Y/%m/', blank=True, null=True, help_text="Attached file/document")
    attachment_name = models.CharField(max_length=255, blank=True, help_text="Original filename")
    attachment_size = models.PositiveIntegerField(blank=True, null=True, help_text="File size in bytes")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.username} to {self.recipient.username}: {self.subject}"
    
    @property
    def has_attachment(self):
        return bool(self.attachment)
    
    def get_file_size_display(self):
        """Format file size for display"""
        if not self.attachment_size:
            return ""
        size = float(self.attachment_size)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_file_extension(self):
        """Get file extension"""
        if self.attachment_name:
            return self.attachment_name.split('.')[-1].lower() if '.' in self.attachment_name else ''
        return ''


class Notification(models.Model):
    """System notifications for users"""
    NOTIFICATION_TYPES = [
        ('application_status', 'Application Status Update'),
        ('mentorship_request', 'Mentorship Request'),
        ('session_scheduled', 'Session Scheduled'),
        ('opportunity_new', 'New Opportunity'),
        ('training_new', 'New Training'),
        ('system', 'System Notification'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='system')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_url = models.URLField(blank=True, help_text="Optional URL to related content")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.title}"


class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=100, blank=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    cover_image = models.ImageField(upload_to='articles/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Event(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    banner = models.ImageField(upload_to='events/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title
