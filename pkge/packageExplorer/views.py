from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Package, Submission
from .forms import PackageSubmissionForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
import os
from django.db.models import Q
import logging
logger = logging.getLogger(__name__)

def view_submissions(request):
    # unified search 
    unified_search = request.GET.get('unified_search', '').strip()
    
    # advanced search
    title_query = request.GET.get('title', '').strip()
    author_query = request.GET.get('author', '').strip()
    tag_query = request.GET.get('tag', '').strip()

    # display all Packages
    packages = Package.objects.filter(approved=True)

    # simple search
    if unified_search:
        packages = packages.filter(
            Q(title__icontains=unified_search) | 
            Q(author__username__icontains=unified_search) | 
            Q(tags__name__icontains=unified_search)
        ).distinct()
    
    # advanced search
    else:
        if title_query:
            packages = packages.filter(title__icontains=title_query)
        if author_query:
            packages = packages.filter(author__username__icontains=author_query)
        if tag_query:
            packages = packages.filter(tags__name__icontains=tag_query).distinct()

    context = {
        'packages': packages,
        'unified_search': unified_search,
        'title_query': title_query,
        'author_query': author_query,
        'tag_query': tag_query,
    }
    return render(request, 'view_submissions.html', context)

@login_required
# save submitted package
def submit_package(request):
    if request.method == 'POST':
        form = PackageSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            package = form.save(commit=True)  
            package.author = request.user
            package.save()  
            return redirect('profile')
    else:
        form = PackageSubmissionForm()

    return render(request, 'submit_package.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'login.html'

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def profile_view(request):
    user_packages = Package.objects.filter(author=request.user)
    return render(request, 'profile.html', {'packages': user_packages})

@login_required
def edit_submission(request, package_id):
    package = get_object_or_404(Package, id=package_id)

    # redirect if not author or admin
    if package.author != request.user and not request.user.is_staff:
        return redirect('view_submissions') 

    if request.method == 'POST':
        form = PackageSubmissionForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            form.save()
            return redirect('profile' if not request.user.is_staff else 'admin_dashboard') 
    else:
        form = PackageSubmissionForm(instance=package)

    return render(request, 'edit_submission.html', {'form': form})


@login_required
def delete_submission(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    
    # redirect if not author or an admin
    if not request.user.is_staff and package.author != request.user:
        return redirect('view_submissions')
    
    if request.method == 'POST':
        # delete thumbnail image from storage
        #TODO: also make changing thumbnail delete old one 
        if package.thumbnail:
            try:
                os.remove(package.thumbnail.path)
                print(f"Thumbnail {package.thumbnail.path} deleted.")
            except Exception as e:
                print(f"Error deleting thumbnail {package.thumbnail.path}: {e}")
        
        package.delete()
        return redirect('profile')

    return render(request, 'delete_submission.html', {'package': package})


@staff_member_required
# admin dashboard only show unapproved submissions
def admin_dashboard(request):
    pending_packages = Package.objects.filter(approved=False)  
    return render(request, 'admin_dashboard.html', {'packages': pending_packages})

@staff_member_required
def approve_package(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    package.approved = True
    package.save()
    return redirect('admin_dashboard')

@staff_member_required
def deny_package(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    package.delete()
    return redirect('admin_dashboard')

@staff_member_required
def admin_edit_submission(request, package_id):
    package = get_object_or_404(Package, id=package_id)

    if request.method == 'POST':
        form = PackageSubmissionForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = PackageSubmissionForm(instance=package)

    return render(request, 'admin_edit_submission.html', {'form': form, 'package': package})

