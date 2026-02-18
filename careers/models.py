from django.conf import settings
from django.db import models
from django.utils.text import slugify


class CareerCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=1, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Career(models.Model):
    category = models.ForeignKey(CareerCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='careers')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    overview = models.TextField()
    skills = models.TextField(help_text="Required skills for this career")
    education_path = models.TextField(help_text="Educational requirements and path")
    institutions = models.TextField(help_text="Recommended institutions")
    future_prospects = models.TextField(help_text="Future career prospects")
    image = models.ImageField(upload_to='careers/', blank=True, null=True)
    RIASEC_CHOICES = [
        ('R', 'Realistic'),
        ('I', 'Investigative'),
        ('A', 'Artistic'),
        ('S', 'Social'),
        ('E', 'Enterprising'),
        ('C', 'Conventional'),
    ]
    riasec_primary = models.CharField(max_length=1, choices=RIASEC_CHOICES, blank=True)
    riasec_secondary = models.CharField(max_length=10, blank=True, help_text="Comma-separated secondary RIASEC codes, e.g. I,A")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title


class CareerProgram(models.Model):
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='programs')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subjects_required = models.TextField(blank=True)
    skills_to_develop = models.TextField(blank=True)
    LEVEL_CHOICES = [
        ('ordinary', 'Ordinary Level (S1-S3)'),
        ('advanced', 'Advanced Level (S4-S6)'),
    ]
    INSTITUTION_CHOICES = [
        ('school', 'School'),
        ('university', 'University'),
    ]
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='advanced')
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_CHOICES, default='university')
    country = models.CharField(max_length=100, default='Rwanda')

    def __str__(self):
        return f"{self.career.title} - {self.name}"


class CareerQuestion(models.Model):
    CATEGORY_CHOICES = [
        ('R', 'Realistic'),
        ('I', 'Investigative'),
        ('A', 'Artistic'),
        ('S', 'Social'),
        ('E', 'Enterprising'),
        ('C', 'Conventional'),
    ]
    prompt = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.get_category_display()} - {self.prompt[:40]}"


class CareerOption(models.Model):
    question = models.ForeignKey(CareerQuestion, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    explanation = models.CharField(max_length=255, blank=True)
    value = models.PositiveSmallIntegerField(default=3)

    def __str__(self):
        return self.text


class CareerOptionWeight(models.Model):
    option = models.ForeignKey(CareerOption, on_delete=models.CASCADE, related_name='career_weights')
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='option_weights')
    weight = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ['option', 'career']

    def __str__(self):
        return f"{self.career.title} - {self.option.text[:20]} ({self.weight})"


class CareerDiscoveryResponse(models.Model):
    session_key = models.CharField(max_length=64)
    level = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Career Discovery {self.session_key}"


class CareerDiscoveryAnswer(models.Model):
    response = models.ForeignKey(CareerDiscoveryResponse, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(CareerQuestion, on_delete=models.CASCADE)
    option = models.ForeignKey(CareerOption, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['response', 'question']

    def __str__(self):
        return f"{self.response.session_key} - {self.question.id}"


class CareerAssessment(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='career_assessments',
    )
    session_key = models.CharField(max_length=64, blank=True)
    level = models.CharField(max_length=20, blank=True)
    date_started = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')

    class Meta:
        ordering = ['-date_started']

    def __str__(self):
        if self.user:
            return f"Assessment #{self.id} for {self.user}"
        return f"Assessment #{self.id} (anonymous)"


class CareerAnswer(models.Model):
    assessment = models.ForeignKey(CareerAssessment, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(CareerQuestion, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ['assessment', 'question']

    def __str__(self):
        return f"{self.assessment_id} - Q{self.question_id}: {self.score}"


class CareerResult(models.Model):
    assessment = models.OneToOneField(CareerAssessment, on_delete=models.CASCADE, related_name='result')
    realistic_score = models.PositiveIntegerField(default=0)
    investigative_score = models.PositiveIntegerField(default=0)
    artistic_score = models.PositiveIntegerField(default=0)
    social_score = models.PositiveIntegerField(default=0)
    enterprising_score = models.PositiveIntegerField(default=0)
    conventional_score = models.PositiveIntegerField(default=0)
    primary_code = models.CharField(max_length=1)
    secondary_code = models.CharField(max_length=1)
    tertiary_code = models.CharField(max_length=1)

    def __str__(self):
        return f"Result {self.primary_code}{self.secondary_code}{self.tertiary_code} for assessment {self.assessment_id}"


class CareerRecommendation(models.Model):
    code = models.CharField(max_length=3, unique=True)
    description = models.TextField()
    suggested_careers = models.TextField(blank=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return self.code
