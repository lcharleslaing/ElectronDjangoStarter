from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import UserPreference
import json

@login_required
@require_http_methods(["GET", "POST"])
def preferences_view(request: HttpRequest):
    prefs, _ = UserPreference.objects.get_or_create(user=request.user)
    if request.method == 'GET':
        return JsonResponse({
            'theme': prefs.theme,
            'last_project_id': prefs.last_project_id,
            'window_bounds': prefs.window_bounds,
            'updated_at': prefs.updated_at.isoformat(),
        })
    # POST
    try:
        data = json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        data = {}
    allowed = {'theme', 'last_project_id', 'window_bounds'}
    for key in allowed:
        if key in data:
            setattr(prefs, key, data[key])
    prefs.save()
    return JsonResponse({'ok': True})
