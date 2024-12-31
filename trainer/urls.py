from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('grammar-options/', views.grammar_options, name='grammar_options'),  # Grammar Options
    path('exercise-options/<str:exercise_type>/', views.exercise_options, name='exercise_options'),
    path('preposition/', views.preposition, name='preposition'),  # Prepositions
    path('articles/', views.articles, name='articles'),
    path('sentence_formation/', views.sentence_formation, name='sentence_formation'),
    path('active_passive/', views.active_passive, name='active_passive'),
    path('direct_indirect/', views.direct_indirect, name='direct_indirect'),
    path('learn/<str:exercise_type>/', views.learn_exercise, name='learn_exercise'),
    path('fillup/<str:question_type>/', views.fillup, name='fillup'),
    ]
