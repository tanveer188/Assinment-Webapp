from django.urls import path,include
from .views import *
urlpatterns = [
  path("dashboard",dashboard,name="dashboard"),
  path('home/',admin_home,name="Admin_homepage"),
  path('class/<str:pk>',class_view,name="class_view"),
  path('staff/',staff_view,name="staff_view"),
  path('Qizzes/<str:pk>',quiz_view,name="quiz_view"),
  path('newclass',newclass,name="newclass"),
  path('newsubject/<str:pk>',newsubject,name="newsubject"),
  path('Edit/<str:model_name>/<str:pk>',Edit,name="Edit"),
  path('delete/',Delete_clas,name="Delete_clas"),
  path('delete-subject/',Delete_subject,name="Delete_subject"),
  path('staff/new',register_teacher,name="register_teacher"),
  path('staff/delete',removeteacher,name="removeteacher"),
  path('remove/quiz',removeQuiz,name="removeQuiz"),
  path('create/quiz/<str:pk>',create_quizz,name="create_quizz"),
  path('create/quiz/step2/<str:pk>',submit_quiz,name="submit_quiz"),
]