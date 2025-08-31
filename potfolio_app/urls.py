# projects/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
urlpatterns = [
    path('', views.home, name='home'),
    path('project/<slug:slug>/', views.project_detail, name='project_detail'),
    path('project/<slug:slug>/download/', views.download_file, name='download_file'),
    path('export_to_word/', views.export_to_word, name='export_to_word'),
    path('login/', views.custom_login, name='login'),
    path('register/', views.register, name='register'),
]
