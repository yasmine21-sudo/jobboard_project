from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator

# --- Core Normalization Models (New/Updated) ---

class Industry(models.Model):
    """Normalized list of industries (e.g., Tech, Finance, Healthcare)."""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Industries"

class JobType(models.Model):
    """Normalized job types (e.g., Full-Time, Part-Time, Contract)."""
    name = models.CharField(max_length=50, unique=True) # e.g., 'Full-Time'
    slug = models.CharField(max_length=50, unique=True) # e.g., 'FULL'
    
    def __str__(self):
        return self.name
    
class Location(models.Model):
    """Normalized list of locations for better consistency (e.g., San Francisco, Remote)."""
    name = models.CharField(max_length=255, unique=True) # E.g., 'San Francisco, CA' or 'Remote'
    
    def __str__(self):
        return self.name

class Skill(models.Model):
    """Centralized list of suggested skills."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# --- Company Model ---
class Company(models.Model):
    """Stores information about the hiring company."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    industry = models.ForeignKey(Industry, related_name='companies', on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey(Location, related_name='companies', on_delete=models.SET_NULL, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    logo_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Companies"


# --- Job Category Model ---
class JobCategory(models.Model):
    """Defines categories for filtering jobs (e.g., Design, Development, Marketing)."""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Job Categories"


# --- Job Model (Updated) ---
class Job(models.Model):
    """The main job listing model."""
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.ForeignKey(Company, related_name='jobs', on_delete=models.CASCADE)
    location = models.ForeignKey(Location, related_name='jobs', on_delete=models.PROTECT) # Changed to FK
    category = models.ForeignKey(JobCategory, related_name='jobs', on_delete=models.SET_NULL, null=True)
    job_type = models.ForeignKey(JobType, related_name='jobs', on_delete=models.PROTECT) # Changed to FK
    salary_min = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    salary_max = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    date_posted = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.company.name}"
    
    class Meta:
        ordering = ['-date_posted']


# --- User Profile (Candidate) Model (Updated) ---
class UserProfile(models.Model):
    """Extends the built-in User model with candidate-specific details."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    # Changed to ManyToManyField for array-like structure with suggestions
    skills = models.ManyToManyField(Skill, related_name='users', blank=True) 
    resume_url = models.URLField(max_length=500, blank=True, null=True) 
    current_title = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Profile for {self.user.username}"


# --- Application Model (Unchanged) ---
class Application(models.Model):
    """Tracks a user's application for a specific job."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('REVIEWED', 'Under Review'),
        ('INTERVIEW', 'Interview Scheduled'),
        ('ACCEPTED', 'Offer Extended'),
        ('REJECTED', 'Rejected'),
    ]

    job = models.ForeignKey(Job, related_name='applications', on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, related_name='applications', on_delete=models.CASCADE)
    date_applied = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    cover_letter = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Application by {self.applicant.username} for {self.job.title}"
    
    class Meta:
        unique_together = ('job', 'applicant')


# --- Saved Job (Bookmark) Model (Unchanged) ---
class SavedJob(models.Model):
    """Allows users to bookmark jobs."""
    user = models.ForeignKey(User, related_name='saved_jobs', on_delete=models.CASCADE)
    job = models.ForeignKey(Job, related_name='saved_by', on_delete=models.CASCADE)
    saved_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"
    
    class Meta:
        unique_together = ('user', 'job')