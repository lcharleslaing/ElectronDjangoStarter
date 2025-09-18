from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Project

@login_required
def project_list(request):
    projects = Project.objects.filter(user=request.user).order_by('-updated_at')
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            Project.objects.create(user=request.user, title=title, description=request.POST.get('description', ''))
            return redirect('projects:list')
    return render(request, 'projects/list.html', { 'projects': projects })

@login_required
@require_http_methods(["GET", "POST"])    
def project_detail(request, pk: int):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'POST':
        if 'delete' in request.POST:
            project.delete()
            return redirect('projects:list')
        project.title = request.POST.get('title', project.title)
        project.description = request.POST.get('description', project.description)
        project.save()
    return render(request, 'projects/detail.html', { 'project': project })
