from django.urls import path
from . import views

urlpatterns = [
    path('projects-list/', views.projects_list, name='projects_list'),
    path('projects-add/', views.projects_add, name='projects_add'),
    path('projects-edit/<int:pk>/', views.projects_edit, name='projects_edit'),
    path('projects-download-files/<int:pk>/', views.projects_download_files, name='projects_download_files'),
]