
from django.contrib import admin
from django.urls import path, include
from . import views
app_name = 'interview'
urlpatterns = [
    path('home/', views.home, name='home'),
    path('ai_interview_options/', views.ai_interview_options, name='ai_interview_options'),
    path('mixed_interview/', views.mixed_interview, name='mixed_interview'),
    path('technical_interview/', views.technical_interview, name='technical_interview'),
    path('general_interview/', views.general_interview, name='general_interview'),
    path('index/<str:interview_type>/', views.index, name='index'),      # Add interview_type parameter
    path('question/<str:interview_type>/', views.question, name='question'),  # Add interview_type
    path('results/', views.results, name='results'),
    path('video_feed/', views.video_feed, name='video_feed'),
]