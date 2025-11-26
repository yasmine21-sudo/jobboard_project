from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'jobs', views.JobViewSet, basename='job')
router.register(r'companies', views.CompanyViewSet, basename='company')
router.register(r'categories', views.JobCategoryViewSet, basename='category')
router.register(r'profiles', views.UserProfileViewSet, basename='profile')
router.register(r'applications', views.ApplicationViewSet, basename='application')
router.register(r'saved-jobs', views.SavedJobViewSet, basename='savedjob')


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]