from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import (
    Company, JobCategory, Job, UserProfile, Application, SavedJob,
    Industry, JobType, Location, Skill
)
from .serializers import (
    CompanySerializer, JobCategorySerializer, JobSerializer, 
    UserProfileSerializer, ApplicationSerializer, SavedJobSerializer,
    IndustrySerializer, JobTypeSerializer, LocationSerializer, SkillSerializer
)

# --- Normalization ViewSets (New) ---

class IndustryViewSet(viewsets.ReadOnlyModelViewSet):
    """Provides a list of suggested industries."""
    queryset = Industry.objects.all().order_by('name')
    serializer_class = IndustrySerializer

class JobTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Provides a list of suggested job types (Full-Time, Contract, etc.)."""
    queryset = JobType.objects.all().order_by('name')
    serializer_class = JobTypeSerializer

class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    """Provides a list of suggested locations."""
    queryset = Location.objects.all().order_by('name')
    serializer_class = LocationSerializer

class SkillViewSet(viewsets.ModelViewSet):
    """
    Provides suggested skills list and allows users to create new skills
    if they don't exist (handled by serializer get_or_create).
    """
    queryset = Skill.objects.all().order_by('name')
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny] # Allow anyone to read the skill list

    # Optional: Filter skills based on a search query
    def get_queryset(self):
        queryset = self.queryset
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset


# --- Core Logic ViewSets (Updated) ---

class JobViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing job listings.
    Allows listing, searching, creating, updating, and deleting jobs.
    """
    queryset = Job.objects.filter(is_active=True)
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = self.queryset

        # --- Search and Filter Logic (Updated to use FK IDs) ---
        query = self.request.query_params.get('q') # Full-text search
        category_id = self.request.query_params.get('category')
        job_type_id = self.request.query_params.get('type') # Now uses ID
        location_id = self.request.query_params.get('location') # Now uses ID

        if query:
            # Search by job title, description, or company name
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(company__name__icontains=query)
            )
        
        if category_id:
            queryset = queryset.filter(category__id=category_id)

        if job_type_id:
            queryset = queryset.filter(job_type__id=job_type_id)

        if location_id:
            queryset = queryset.filter(location__id=location_id)

        return queryset


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing company details. Read-only for public access.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class JobCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing job categories. Read-only.
    """
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user profiles.
    Users can only view/edit their own profile.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return UserProfile.objects.filter(user=self.request.user)
        return UserProfile.objects.none()

    def perform_create(self, serializer):
        # Automatically link the profile to the currently logged-in user
        serializer.save(user=self.request.user)


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing job applications.
    """
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(applicant=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

    
class SavedJobViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing a user's saved jobs (bookmarks).
    """
    queryset = SavedJob.objects.all()
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['delete'], url_path='unsave/(?P<job_id>[^/.]+)')
    def unsave(self, request, job_id=None):
        try:
            saved_job = SavedJob.objects.get(user=request.user, job_id=job_id)
            saved_job.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SavedJob.DoesNotExist:
            return Response({"detail": "Job not found in saved list."}, status=status.HTTP_404_NOT_FOUND)