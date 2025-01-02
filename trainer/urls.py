from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
    path("", views.login, name="login"),
    path("home/", views.home, name="home"),  # Home page
    path("signup/", views.signup, name="signup"),
    path(
        "grammar-options/", views.grammar_options, name="grammar_options"
    ),  # Grammar Options
    path(
        "vocab-options/", views.vocab_options, name="vocab_options"
    ),  # Vocabulary Options
    path("vocab_learn/", views.vocab_learn, name="vocab_learn"),  # Vocabulary Learn
    path("vocabulary/", views.vocabulary, name="vocabulary"),  # Vocabulary
    path(
        "exercise-options/<str:exercise_type>/",
        views.exercise_options,
        name="exercise_options",
    ),
    path("preposition/", views.preposition, name="preposition"),  # Prepositions
    path("articles/", views.articles, name="articles"),
    path("sentence_formation/", views.sentence_formation, name="sentence_formation"),
    path("active_passive/", views.active_passive, name="active_passive"),
    path("direct_indirect/", views.direct_indirect, name="direct_indirect"),
    path("learn/<str:exercise_type>/", views.learn_exercise, name="learn_exercise"),
    path("fillup/<str:question_type>/", views.fillup, name="fillup"),
    path("speaking/", views.speaking, name="speaking"),
    path(
        "generate_speaking_statement/",
        views.generate_speaking_statement,
        name="generate_speaking_statement",
    ),
    path("conjunctions/", views.conjunctions, name="conjunctions"),
    path("interjections/", views.interjections, name="interjections"),
    path("nouns/", views.nouns, name="nouns"),
    path("pronouns/", views.pronouns, name="pronouns"),
    path("tenses/", views.tenses, name="tenses"),
    path("verbs_adverbs/", views.verbs_adverbs, name="verbs_adverbs"),
    path("adjectives/", views.adjectives, name="adjectives"),
]
=======
    path('', views.home, name='home'),  # Home page
    path('grammar-options/', views.grammar_options, name='grammar_options'),  # Grammar Options
    path('vocab-options/', views.vocab_options, name='vocab_options'),  # Vocabulary Options
    path('vocab_learn/', views.vocab_learn, name='vocab_learn'),  # Vocabulary Learn
    path('vocabulary/', views.vocabulary, name='vocabulary'),  # Vocabulary
    path('exercise-options/<str:exercise_type>/', views.exercise_options, name='exercise_options'),
    path('preposition/', views.preposition, name='preposition'),  # Prepositions
    path('articles/', views.articles, name='articles'),
    path('sentence_formation/', views.sentence_formation, name='sentence_formation'),
    path('active_passive/', views.active_passive, name='active_passive'),
    path('direct_indirect/', views.direct_indirect, name='direct_indirect'),
    path('learn/<str:exercise_type>/', views.learn_exercise, name='learn_exercise'),
    path('fillup/<str:question_type>/', views.fillup, name='fillup'),
    path('speaking/', views.speaking, name='speaking'),
    path('generate_speaking_statement/', views.generate_speaking_statement, name='generate_speaking_statement'),
    path('conjunctions/', views.conjunctions, name='conjunctions'),
    path('interjections/', views.interjections, name='interjections'),
    path('nouns/', views.nouns, name='nouns'),
    path('pronouns/', views.pronouns, name='pronouns'),
    path('tenses/', views.tenses, name='tenses'),
    path('verbs_adverbs/', views.verbs_adverbs, name='verbs_adverbs'),
    path('adjectives/', views.adjectives, name='adjectives'),
    path('mock_test/<str:exercise_type>/', views.mock_test, name='mock_test'),
    path('mock_test_submit/<str:exercise_type>/', views.handle_mock_test_submit, name='mock_test_submit'),
 ]
>>>>>>> upstream/Aravind
