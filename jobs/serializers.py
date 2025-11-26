from rest_framework import serializers
from .models import Company, JobCategory, Job, UserProfile, Application, SavedJob
from django.contrib.auth.models import User

# --- Nested Serializers ---

class CompanySerializer(serializers.ModelSerializer):
    """Serializer for the Company model."""
    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ('id',)

class JobCategorySerializer(serializers.ModelSerializer):
    """Serializer for the JobCategory model."""
    class Meta:
        model = JobCategory
        fields = ['id', 'name']


# --- Main Data Serializers ---

class JobSerializer(serializers.ModelSerializer):
    """Serializer for the Job model, including nested Company and Category data."""
    company = CompanySerializer(read_only=True)
    category = JobCategorySerializer(read_only=True)
    # Custom field to allow writing using the company ID and category ID
    company_id = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), source='company', write_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=JobCategory.objects.all(), source='category', write_only=True, allow_null=True)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'location', 'job_type', 
            'salary_min', 'salary_max', 'date_posted', 'is_active', 
            'company', 'category', 'company_id', 'category_id' # Used for POST/PUT
        ]
        read_only_fields = ('id', 'date_posted')


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for the UserProfile, including basic User info."""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'bio', 'phone_number', 
            'skills', 'resume_url', 'current_title'
        ]


class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for tracking job applications."""
    applicant_username = serializers.CharField(source='applicant.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'job', 'applicant', 'job_title', 'applicant_username', 
            'date_applied', 'status', 'cover_letter'
        ]
        read_only_fields = ('applicant', 'date_applied', 'status') # Applicant is set automatically in the view


class SavedJobSerializer(serializers.ModelSerializer):
    """Serializer for saving/bookmarking jobs."""
    job_details = JobSerializer(source='job', read_only=True)

    class Meta:
        model = SavedJob
        fields = ['id', 'job', 'user', 'saved_at', 'job_details']
        read_only_fields = ('user', 'saved_at') # User is set automatically in the view