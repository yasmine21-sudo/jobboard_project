from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Company, JobCategory, Job, UserProfile, Application, SavedJob
from .serializers import (
    CompanySerializer, JobCategorySerializer, JobSerializer, 
    UserProfileSerializer, ApplicationSerializer, SavedJobSerializer
)


class JobViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing job listings.
    Allows listing, searching, creating, updating, and deleting jobs.
    """
    queryset = Job.objects.filter(is_active=True)
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Only authenticated users can create/edit

    def get_queryset(self):
        # Base queryset for active jobs
        queryset = self.queryset

        # --- Search and Filter Logic ---
        query = self.request.query_params.get('q') # Full-text search
        category_id = self.request.query_params.get('category')
        job_type = self.request.query_params.get('type')

        if query:
            # Search by job title, description, or company name
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(company__name__icontains=query) |
                Q(location__icontains=query)
            )
        
        if category_id:
            queryset = queryset.filter(category__id=category_id)

        if job_type:
            queryset = queryset.filter(job_type__iexact=job_type)

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
        # Ensure a user can only access their own profile
        if self.request.user.is_authenticated:
            return UserProfile.objects.filter(user=self.request.user)
        return UserProfile.objects.none()

    def perform_create(self, serializer):
        # Automatically link the profile to the currently logged-in user
        serializer.save(user=self.request.user)


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing job applications.
    Users can create applications and view their own applications.
    """
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Candidates can only see their own applications
        return Application.objects.filter(applicant=self.request.user)
    
    def perform_create(self, serializer):
        # Set the applicant to the current user
        try:
            serializer.save(applicant=self.request.user)
        except Exception as e:
            return Response({"detail": f"Application failed: {e}"}, status=status.HTTP_400_BAD_REQUEST)

    
class SavedJobViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing a user's saved jobs (bookmarks).
    """
    queryset = SavedJob.objects.all()
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own saved jobs
        return SavedJob.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Set the user to the current user
        serializer.save(user=self.request.user)

    # Optional: Custom action to quickly unsave a job by its ID
    @action(detail=False, methods=['delete'], url_path='unsave/(?P<job_id>[^/.]+)')
    def unsave(self, request, job_id=None):
        try:
            saved_job = SavedJob.objects.get(user=request.user, job_id=job_id)
            saved_job.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SavedJob.DoesNotExist:
            return Response({"detail": "Job not found in saved list."}, status=status.HTTP_404_NOT_FOUND)