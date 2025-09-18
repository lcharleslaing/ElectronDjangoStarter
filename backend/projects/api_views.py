from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Project
import json

@login_required
@require_http_methods(["GET", "POST"])
def project_list_api(request: HttpRequest):
    if request.method == 'GET':
        items = list(Project.objects.filter(user=request.user).order_by('-updated_at').values())
        return JsonResponse(items, safe=False)
    data = json.loads(request.body.decode('utf-8') or '{}')
    title = data.get('title')
    if not title:
        return JsonResponse({ 'error': 'title required' }, status=400)
    p = Project.objects.create(user=request.user, title=title, description=data.get('description',''), data=data.get('data', {}))
    return JsonResponse({ 'id': p.id }, status=201)

@login_required
@require_http_methods(["GET", "PUT", "DELETE"])    
def project_detail_api(request: HttpRequest, pk: int):
    p = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'GET':
        return JsonResponse({
            'id': p.id,
            'title': p.title,
            'description': p.description,
            'data': p.data,
            'created_at': p.created_at.isoformat(),
            'updated_at': p.updated_at.isoformat(),
        })
    if request.method == 'DELETE':
        p.delete()
        return JsonResponse({ 'ok': True })
    # PUT
    data = json.loads(request.body.decode('utf-8') or '{}')
    for key in ['title', 'description', 'data']:
        if key in data:
            setattr(p, key, data[key])
    p.save()
    return JsonResponse({ 'ok': True })
