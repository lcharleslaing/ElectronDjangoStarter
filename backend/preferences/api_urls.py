from django.urls import path
from .views import preferences_view

urlpatterns = [
    path('preferences/', preferences_view, name='preferences'),
]
