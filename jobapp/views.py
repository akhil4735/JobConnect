from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .models import *

# Home Page View
def home(request):
    return render(request, 'home.html')

# Register View (Manual Form Handling)
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('register')

        user = User.objects.create_user(username=username, password=password1)
        Profile.objects.create(user=user)  # Create empty profile
        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')

    return render(request, 'register.html')

# Login View (Manual Authentication)
def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password!")
    
    return render(request, 'login.html')

# Logout View
@login_required(login_url='/login/')
def user_logout(request):
    logout(request)
    messages.success(request, "You have logged out successfully!")
    return redirect('login')

# Job List View
@login_required(login_url='/login/')
def job_list(request):
    search_query = request.GET.get('search','')
    jobs = Job.objects.all()
    if search_query:
        jobs = jobs.filter(title__icontains=search_query)

    return render(request, 'job_list.html', {'jobs': jobs})

@login_required(login_url='/login/')
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'job_detail.html', {'job': job})

# Post Job View (Manual Form Handling)
@login_required(login_url='/login/')
def post_job(request):
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        location = request.POST['location']
        salary = request.POST.get('salary', None)
        category = request.POST.get('category', '') 
        job_type = request.POST.get('job_type', 'Full-Time') 
        company=request.POST.get('company',None)

        job = Job.objects.create(
            title=title,
            description=description,
            location=location,
            salary=salary if salary else None, 
            category=category,
            job_type=job_type,
            posted_by=request.user,
            company=company
        )

        messages.success(request, "Job posted successfully!")
        return redirect('job_list')

    return render(request, 'postjob.html')

# Apply for Job View (Manual Form Handling)
@login_required(login_url='/login/')
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":
        cover_letter = request.POST['cover_letter']
        resume_file = request.FILES['resume']

        JobApplication.objects.create(
            job=job,
            applicant=request.user,
            resume=resume_file,
            cover_letter=cover_letter
        )
        messages.success(request, "Job application submitted successfully!")
        return redirect('job_list')

    return render(request, 'applyjob.html', {'job': job})

# View Applied Jobs
@login_required(login_url='/login/')
def my_applications(request):
    applications = JobApplication.objects.filter(applicant=request.user)
    return render(request, 'myapplications.html', {'applications': applications})

# Profile View with Update functionality
@login_required(login_url='/login/')
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update profile information
        profile.email = request.POST.get('email', '')
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.bio = request.POST.get('bio', '')
        profile.skills = request.POST.get('skills', '')
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    
    return render(request, 'profile.html', {'profile': profile})

# View Applications for Jobs I Posted
@login_required(login_url='/login/')
def my_posted_jobs(request):
    # Get all jobs posted by the current user
    posted_jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')
    
    # Get applications for each job
    job_applications = {}
    for job in posted_jobs:
        applications = JobApplication.objects.filter(job=job).order_by('-applied_at')
        job_applications[job.id] = applications
    
    return render(request, 'my_posted_jobs.html', {
        'posted_jobs': posted_jobs,
        'job_applications': job_applications
    })

# Accept/Reject Application
@login_required(login_url='/login/')
def update_application_status(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(JobApplication, id=application_id)
        
        # Check if the current user is the job poster
        if application.job.posted_by != request.user:
            messages.error(request, "You don't have permission to update this application!")
            return redirect('my_posted_jobs')
        
        status = request.POST.get('status')
        if status in ['Accepted', 'Rejected', 'Pending']:
            application.application_status = status
            application.save()
            messages.success(request, f"Application status updated to {status}")
        else:
            messages.error(request, "Invalid status!")
    
    return redirect('my_posted_jobs')

# Dashboard View
@login_required(login_url='/login/')
def dashboard(request):
    # Get user's applications
    my_applications = JobApplication.objects.filter(applicant=request.user).order_by('-applied_at')[:5]
    
    # Get jobs posted by user
    posted_jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')[:5]
    
    # Get applications for user's posted jobs
    total_applications = 0
    for job in posted_jobs:
        total_applications += JobApplication.objects.filter(job=job).count()
    
    context = {
        'my_applications': my_applications,
        'posted_jobs': posted_jobs,
        'total_applications': total_applications,
        'total_posted_jobs': posted_jobs.count(),
        'total_my_applications': my_applications.count(),
    }
    
    return render(request, 'dashboard.html', context)

@login_required(login_url='/login/')
def view_application(request, application_id):
    # Get the job application based on the provided application_id
    application = get_object_or_404(JobApplication, id=application_id)

    return render(request, 'view_application.html', {'application': application})

