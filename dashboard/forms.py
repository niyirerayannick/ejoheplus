from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import StudentCV, Message, Article, Event
from accounts.models import User
from careers.models import Career
from training.models import Course, CourseMaterial, Enrollment, Certificate
from mentorship.models import MentorshipConnection
from opportunities.models import Opportunity


class CVForm(forms.ModelForm):
    class Meta:
        model = StudentCV
        fields = [
            'full_name', 'email', 'phone', 'address', 'linkedin_url', 
            'website_url', 'summary', 'skills', 'languages'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'website_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 5
            }),
            'skills': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'e.g., Python, JavaScript, Leadership'
            }),
            'languages': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'e.g., English, French, Spanish'
            }),
        }


class MessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.none(),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
        })
    )
    
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'body': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 8
            }),
        }
    
    def __init__(self, *args, **kwargs):
        sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
        if sender:
            # Students can message mentors and admins
            # Mentors can message students and admins
            # Partners can message students, mentors, and admins
            if sender.is_student:
                self.fields['recipient'].queryset = User.objects.filter(role__in=['mentor', 'admin'])
            elif sender.is_mentor:
                self.fields['recipient'].queryset = User.objects.filter(role__in=['student', 'admin'])
            elif sender.is_partner:
                self.fields['recipient'].queryset = User.objects.filter(role__in=['student', 'mentor', 'admin'])


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'category', 'tags', 'excerpt', 'content', 'cover_image', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'category': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'tags': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'placeholder': 'e.g., Education, Skills'}),
            'excerpt': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 8}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
        }


class AdminArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['author', 'title', 'category', 'tags', 'excerpt', 'content', 'cover_image', 'status']
        widgets = {
            'author': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'category': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'tags': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'placeholder': 'e.g., Education, Skills'}),
            'excerpt': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 8}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
        }


class EventForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'})
    )
    end_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'})
    )

    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'start_date', 'end_date', 'banner', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 6}),
            'location': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
        }


class CourseCreateForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'category', 'description', 'overview', 'duration_hours', 'level', 'price', 'is_free', 'thumbnail', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'category': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 4}),
            'overview': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 6}),
            'duration_hours': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'level': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'step': '0.01'}),
            'is_free': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded'}),
            'thumbnail': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded'}),
        }


class AdminCourseForm(forms.ModelForm):
    slug = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}))

    class Meta:
        model = Course
        fields = ['title', 'slug', 'category', 'description', 'overview', 'instructor', 'created_by', 'duration_hours', 'level', 'price', 'is_free', 'thumbnail', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'category': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 4}),
            'overview': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 6}),
            'instructor': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'created_by': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'level': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'step': '0.01'}),
            'is_free': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded'}),
            'thumbnail': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded'}),
        }


class OpportunityCreateForm(forms.ModelForm):
    slug = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}))

    class Meta:
        model = Opportunity
        fields = ['title', 'slug', 'type', 'category', 'description', 'requirements', 'benefits', 'deadline', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'type': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'category': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 4}),
            'requirements': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 4}),
            'benefits': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 3}),
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded'}),
        }


class AdminOpportunityForm(forms.ModelForm):
    slug = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}))

    class Meta:
        model = Opportunity
        fields = ['title', 'slug', 'type', 'category', 'description', 'requirements', 'benefits', 'deadline', 'created_by', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'type': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'category': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 4}),
            'requirements': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 4}),
            'benefits': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 3}),
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'created_by': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded'}),
        }


class CareerForm(forms.ModelForm):
    slug = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}))

    class Meta:
        model = Career
        fields = ['title', 'slug', 'overview', 'skills', 'education_path', 'institutions', 'future_prospects', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'overview': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 4}),
            'skills': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 3}),
            'education_path': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 3}),
            'institutions': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 3}),
            'future_prospects': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
        }


class AdminUserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'})


class AdminUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_mentor_approved', 'phone', 'bio', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'role': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded'}),
            'is_mentor_approved': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'bio': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
        }


class AdminMentorCreateForm(AdminUserCreateForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'mentor'
        user.is_mentor_approved = True
        if commit:
            user.save()
        return user


class AdminCourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['course', 'title', 'material_type', 'content', 'video_url', 'file', 'order', 'is_free']
        widgets = {
            'course': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'material_type': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'content': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 4}),
            'video_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'file': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'is_free': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded'}),
        }


class AdminEnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['course', 'student', 'completed_at', 'is_completed']
        widgets = {
            'course': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'student': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'completed_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = User.objects.filter(role='student')


class AdminCertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['enrollment', 'certificate_id']
        widgets = {
            'enrollment': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'certificate_id': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
        }


class AdminMentorAssignmentForm(forms.ModelForm):
    class Meta:
        model = MentorshipConnection
        fields = ['mentor', 'mentee', 'notes']
        widgets = {
            'mentor': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'mentee': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mentor'].queryset = User.objects.filter(role='mentor', is_active=True, is_mentor_approved=True)
        self.fields['mentee'].queryset = User.objects.filter(role='student', is_active=True)

class StudentCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        user.is_mentor_approved = True
        if commit:
            user.save()
        return user
