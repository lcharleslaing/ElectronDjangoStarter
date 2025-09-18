from django.urls import path
from .api_views import project_list_api, project_detail_api

urlpatterns = [
    path('projects/', project_list_api, name='api_projects'),
    path('projects/<int:pk>/', project_detail_api, name='api_project_detail'),
]
