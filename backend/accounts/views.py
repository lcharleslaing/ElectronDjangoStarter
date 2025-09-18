from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from .forms import RegisterForm, LoginForm

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('projects:list')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        remember = form.cleaned_data.get('remember_me')
        if remember:
            request.session.set_expiry(60 * 60 * 24 * 30)
        else:
            request.session.set_expiry(0)
        return redirect('projects:list')
    return render(request, 'accounts/login.html', { 'form': form })

@login_required
@require_http_methods(["POST"])    
def logout_view(request):
    logout(request)
    return redirect('accounts:login')

@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect('projects:list')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user: User = form.save()
        login(request, user)
        return redirect('projects:list')
    return render(request, 'accounts/register.html', { 'form': form })
