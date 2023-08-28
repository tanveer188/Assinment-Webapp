from django.urls import path,include
from .views import *
urlpatterns = [
  path('quiz/takes/<str:pk>',take_quiz,name="take_quiz"),
  path('quiz/result/<str:pk>',student_quiz_results,name="student_quiz_results"),
]