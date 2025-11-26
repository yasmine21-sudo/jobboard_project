from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints for the jobs application
    path('api/v1/', include('jobs.urls')),
    
    # API endpoints for User Registration, Login, and Management (provided by djoser)
    # The endpoints will be:
    # /api/v1/auth/users/ -> POST for registration
    # /api/v1/auth/token/login/ -> POST for login, returns token
    # /api/v1/auth/token/logout/ -> POST for logout
    path('api/v1/auth/', include('djoser.urls')),
    path('api/v1/auth/', include('djoser.urls.authtoken')),

    # DRF browser authentication (optional, for viewing API in browser)
    path('api/auth-browsable/', include('rest_framework.urls', namespace='rest_framework')), 
]