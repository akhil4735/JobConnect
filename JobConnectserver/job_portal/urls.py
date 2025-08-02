"""
URL configuration for job_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib import admin
from jobapp.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),                         # Home Page
    path('register/', register, name='register'),        # Register User
    path('login/', user_login, name='login'),           # Login Page
    path('logout/', user_logout, name='logout'), 
    path('admin/', admin.site.urls),       # Logout User

    path('job_list/', job_list, name='job_list'),       # List Jobs
    path('<int:job_id>/', job_detail, name='job_detail'),  # Job Detail
    path('post/', post_job, name='post_job'),           # Post a Job
    path('apply/<int:job_id>/', apply_job, name='apply_job'),  # Apply for a Job

    path('profile/', profile, name='profile'),          # User Profile
    path('view-application/<int:application_id>/', view_application, name='view_application'),

    path('my-applications/', my_applications, name='my_applications'),
    path('my-posted-jobs/', my_posted_jobs, name='my_posted_jobs'),
    path('update-application-status/<int:application_id>/', update_application_status, name='update_application_status'),
    path('dashboard/', dashboard, name='dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
