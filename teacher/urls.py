from django.urls import path,include

from .views import *

urlpatterns = [
    path('teacher/home/', teacher_home, name='teacher_home'),
    path('teacher/class/<str:pk>/', class_teacher, name='class_teacher'),
    path('teacher/quiz/<str:pk>/', quiz_teacher, name='quiz_teacher'),
    path('teacher/quiz/check/<str:student_pk>/<str:pk>/', check_quiz, name='check_quiz'),
    path('quiz/<int:pk>/taken_quizzes/', quiz_taken_quizzes, name='quiz_taken_quizzes'),
]
