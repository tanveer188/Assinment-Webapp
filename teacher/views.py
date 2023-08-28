from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib import messages
from teacher.models import Quiz, Student, TakenQuiz, Question,StudentJustificationAnswer

from authentication.models import ClassModel,SubjectModel,TeacherModel
from authentication.decorators import group_required
from django.db import transaction
from django.db.models import Count, Sum
from django.db.models.functions import Concat
from django.contrib.auth import get_user_model
from .forms import ScoreForm
# Create your views here.

User = get_user_model()


@group_required("teacher_grp",redirect_url='home')
def teacher_home(request):
  teacher = request.user.teacher
  subjects = SubjectModel.objects.filter(teacher=teacher)
  classes = ClassModel.objects.filter(subjectmodel__in=subjects).distinct()
  context = {
    "classes":classes
  }
  return render(request,'Admin/home.html',context)

@group_required("teacher_grp",redirect_url='home')
def class_teacher(request,pk):
  class_obj = get_object_or_404(ClassModel, pk=pk)
  teacher = request.user.teacher
  subjects = SubjectModel.objects.filter(class_name=class_obj, teacher=teacher)
  context = {
    "class_name":class_obj,
    "subjects":subjects
  }
  return render(request,'Admin/class.html',context)


@group_required("teacher_grp",redirect_url='home')
def quiz_teacher(request,pk):
  teacher = request.user.teacher
  subject = get_object_or_404(SubjectModel,pk=pk,teacher=teacher)
  quizzes = subject.quizzes.all()
  context = {
    "quizzes":quizzes,
    "pk":pk
  }
  return render(request,"Admin/quiz.html",context)



@group_required("teacher_grp","admin_grp", redirect_url='home')
def check_quiz(request, student_pk, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    student = get_object_or_404(Student, pk=student_pk)
    
    if student.taken_quizzes.filter(quiz=quiz, is_checked=True,student=student).exists():
        return redirect("quiz_taken_quizzes",pk)

    total_questions = quiz.questions.filter(question_type="justification").count()  # Total count of questions in the quiz
    answer_questions = student.get_justification_questions(quiz)  # Get answered questions specific to this quiz
    total_answer_questions = answer_questions.count()  # Count of answered questions

    progress = 100 - round(((total_answer_questions - 1) / total_questions) * 100)  # Calculate progress as a percentage

    question = answer_questions.first()  # Get the first answered question
    instance = StudentJustificationAnswer.objects.get(question=question,student=student)
    if request.method == 'POST':
        form = ScoreForm(instance=instance, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                student_answer = form.save()
                if student.get_justification_questions(quiz).exists():
                    return redirect('check_quiz',student_pk=student_pk, pk=pk)
                else:
                    taken_quizzes = student.taken_quizzes.get(quiz=quiz,is_checked=False)
                    taken_quizzes.is_checked = True
                    taken_quizzes.calculate_score_and_percentage()
                    taken_quizzes.save()
                    return redirect("check_quiz",student_pk=student_pk, pk=pk)

    else:
        form = ScoreForm(instance=instance)

    return render(request, 'teacher/check_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        "answer_model":instance,
        'form': form,
        'progress': progress,
        'answered_questions': total_questions - total_answer_questions,
        'total_questions': total_questions
    })  # Render the quiz form template, passing relevant variables and data to be displayed in the template

@group_required("teacher_grp","admin_grp", redirect_url='home')
def quiz_taken_quizzes(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    taken_quizzes = TakenQuiz.objects.filter(quiz=quiz)
    return render(request, 'teacher/quiz_taken_quizzes.html', {'quiz': quiz, 'taken_quizzes': taken_quizzes})
