from rest_framework import serializers
from .models import (
    Company, JobCategory, Job, UserProfile, Application, SavedJob,
    Industry, JobType, Location, Skill
)
from django.contrib.auth.models import User
from django.db import transaction

# --- Normalization Serializers (New) ---

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = '__all__'

class JobTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobType
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

# --- Nested & Core Serializers (Updated) ---

class CompanySerializer(serializers.ModelSerializer):
    """Serializer for the Company model, now with nested FKs."""
    industry = IndustrySerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    
    # Writeable fields for FK IDs
    industry_id = serializers.PrimaryKeyRelatedField(queryset=Industry.objects.all(), source='industry', write_only=True, allow_null=True)
    location_id = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(), source='location', write_only=True, allow_null=True)

    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ('id',)


class JobCategorySerializer(serializers.ModelSerializer):
    """Serializer for the JobCategory model."""
    class Meta:
        model = JobCategory
        fields = ['id', 'name']


class JobSerializer(serializers.ModelSerializer):
    """Serializer for the Job model, updated with new FKs."""
    company = CompanySerializer(read_only=True)
    category = JobCategorySerializer(read_only=True)
    location = LocationSerializer(read_only=True) # Nested read-only
    job_type = JobTypeSerializer(read_only=True) # Nested read-only

    # Writeable fields for FK IDs
    company_id = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), source='company', write_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=JobCategory.objects.all(), source='category', write_only=True, allow_null=True)
    location_id = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(), source='location', write_only=True)
    job_type_id = serializers.PrimaryKeyRelatedField(queryset=JobType.objects.all(), source='job_type', write_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'salary_min', 'salary_max', 
            'date_posted', 'is_active', 
            'company', 'category', 'location', 'job_type', 
            'company_id', 'category_id', 'location_id', 'job_type_id'
        ]
        read_only_fields = ('id', 'date_posted')


class UserProfileSerializer(serializers.ModelSerializer):
    """UserProfile Serializer, now handling ManyToMany Skills."""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    # Skills are represented by their name/id in the array
    skills = SkillSerializer(many=True, read_only=True)
    
    # Field for writing (input) skills using a list of IDs or names
    # We will use a custom field to handle creation of new skills
    skill_names = serializers.ListField(
        child=serializers.CharField(max_length=100), 
        write_only=True, 
        required=False, 
        help_text="List of skill names. New skills will be created if they don't exist."
    )

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'bio', 'phone_number', 
            'skills', 'skill_names', 'resume_url', 'current_title'
        ]
        read_only_fields = ('id',)

    @transaction.atomic
    def update(self, instance, validated_data):
        # Handle custom skill creation/association during update
        skill_names = validated_data.pop('skill_names', None)

        # Update core profile fields
        super().update(instance, validated_data)

        if skill_names is not None:
            # Get existing skills or create new ones
            skill_objects = []
            for name in skill_names:
                skill, created = Skill.objects.get_or_create(name=name.strip().lower(), defaults={'name': name.strip()})
                skill_objects.append(skill)
            
            # Set the skills for the user profile (clears existing and sets new ones)
            instance.skills.set(skill_objects)

        return instance
    
    @transaction.atomic
    def create(self, validated_data):
        # Handle skill creation during initial profile creation (if user model is not created here)
        skill_names = validated_data.pop('skill_names', None)
        
        # Create core profile
        profile = super().create(validated_data)

        if skill_names is not None:
             skill_objects = []
             for name in skill_names:
                skill, created = Skill.objects.get_or_create(name=name.strip().lower(), defaults={'name': name.strip()})
                skill_objects.append(skill)
             profile.skills.set(skill_objects)

        return profile


class ApplicationSerializer(serializers.ModelSerializer):
    # ... (rest remains the same)
    applicant_username = serializers.CharField(source='applicant.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'job', 'applicant', 'job_title', 'applicant_username', 
            'date_applied', 'status', 'cover_letter'
        ]
        read_only_fields = ('applicant', 'date_applied', 'status')


class SavedJobSerializer(serializers.ModelSerializer):
    # ... (rest remains the same)
    job_details = JobSerializer(source='job', read_only=True)

    class Meta:
        model = SavedJob
        fields = ['id', 'job', 'user', 'saved_at', 'job_details']
        read_only_fields = ('user', 'saved_at')