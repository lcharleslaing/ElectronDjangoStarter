from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.shortcuts import redirect

def health(_):
    return JsonResponse({"ok": True})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health, name='health'),
    path('auth/', include('accounts.urls')),
    path('projects/', include('projects.urls')), 
    path('api/', include('preferences.api_urls')),
    path('api/', include('projects.api_urls')),
    # Back-compat redirects for old default auth paths
    path('accounts/login/', lambda r: redirect('accounts:login'), name='accounts_login_redirect'),
    path('accounts/register/', lambda r: redirect('accounts:register'), name='accounts_register_redirect'),
    path('accounts/logout/', lambda r: redirect('accounts:login'), name='accounts_logout_redirect'),
    path('', lambda r: redirect('projects:list'), name='home'),
]
