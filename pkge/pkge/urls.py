"""
URL configuration for pkge project.

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
from django.contrib import admin
from django.urls import path
from packageExplorer import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('view_submissions/', views.view_submissions, name='view_submissions'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/approve/<int:package_id>/', views.approve_package, name='approve_package'),
    path('admin/deny/<int:package_id>/', views.deny_package, name='deny_package'),
    path('admin/edit/<int:package_id>/', views.admin_edit_submission, name='admin_edit_submission'),
    path('admin/', admin.site.urls),
    path('', views.view_submissions, name='view_submissions'),
    path('submit/', views.submit_package, name='submit_package'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='view_submissions'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('submission/edit/<int:package_id>/', views.edit_submission, name='edit_submission'),
    path('submission/delete/<int:package_id>/', views.delete_submission, name='delete_submission'),  
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

