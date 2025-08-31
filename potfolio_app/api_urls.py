from django.urls import path
from .api_views import project_list, project_detail, submit_feedback, download_file

urlpatterns = [
    path('projects/', project_list, name='project-list'),
    path('projects/<slug:slug>/', project_detail, name='project-detail'),
    path('feedback/', submit_feedback, name='submit-feedback'),
    path('projects/<slug:slug>/download/', download_file, name='download-file'),
]
