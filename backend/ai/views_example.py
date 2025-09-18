# Example (not wired): safe server-side OpenAI usage
# from django.views.decorators.http import require_POST
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from .services import get_openai
# import json
#
# @login_required
# @require_POST
# def generate_example(request):
#     client = get_openai()
#     if client is None:
#         return JsonResponse({ 'error': 'OPENAI_API_KEY not configured' }, status=400)
#     data = json.loads(request.body.decode('utf-8') or '{}')
#     prompt = data.get('prompt', 'Hello')
#     # Example: call a models API here
#     # result = client.chat.completions.create(model='gpt-4o-mini', messages=[{"role":"user","content":prompt}])
#     # return JsonResponse({ 'text': result.choices[0].message['content'] })
#     return JsonResponse({ 'ok': True })
