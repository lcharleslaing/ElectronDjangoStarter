from django.urls import path
from .views import project_list, project_detail

app_name = 'projects'

urlpatterns = [
    path('', project_list, name='list'),
    path('<int:pk>/', project_detail, name='detail'),
]
