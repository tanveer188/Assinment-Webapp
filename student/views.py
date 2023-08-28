from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib import messages
from authentication.models import ClassModel,SubjectModel,TeacherModel
from teacher.models import Quiz, Student, TakenQuiz, Question,StudentJustificationAnswer

from authentication.decorators import group_required
from .forms import  TakeQuizForm,TakeJustificationForm
from django.db import transaction
from django.db.models import Count, Sum
from django.db.models.functions import Concat
from django.contrib.auth import get_user_model

# Create your views here.

User = get_user_model()


@group_required("student_grp",redirect_url='home')
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)  # Retrieve the Quiz object based on the given primary key (pk)
    
    if quiz.are_all_questions_quiz():
      is_checked = True
    else:
      is_checked = False
    student = request.user.student  # Get the student object associated with the currently authenticated user

    if student.quizzes.filter(pk=pk).exists():
        return redirect("student_quiz_results",pk=quiz.id)  # Render a template for a "taken quiz" page if the student has already taken the quiz

    total_questions = quiz.questions.count()  # Total count of questions in the quiz
    unanswered_questions = student.get_unanswered_questions(quiz)  # Get unanswered questions specific to this quiz
    total_unanswered_questions = unanswered_questions.count()  # Count of unanswered questions

    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)  # Calculate progress as a percentage

    question = unanswered_questions.first()  # Get the first unanswered question

    if request.method == 'POST':
      if question.question_type == "quiz":
        print(request.POST)
        form = TakeQuizForm(question=question, data=request.POST)  # Create a form instance with the question and submitted data

        if form.is_valid():  # Check if the form is valid
            with transaction.atomic():
                student_answer = form.save(commit=False)  # Save the student's answer to the current question without committing to the database
                student_answer.question = question
                student_answer.student = student  # Associate the student with the answer
                student_answer.save()  # Save the answer to the database

                if student.get_unanswered_questions(quiz).exists():  # If there are more unanswered questions
                    return redirect('take_quiz', pk)  # Redirect to the same quiz page to answer the next question
                else:
                    takenquiz = TakenQuiz.objects.create(student=student, quiz=quiz,is_checked=is_checked)
                    performance = takenquiz.calculate_score_and_percentage()
                    student.update_score()

                    return redirect('student_quiz_results', pk)  # Redirect to the student's quiz results page
      else:
        form = TakeJustificationForm(question=question, data=request.POST)  # Create a form instance with the question and submitted data

        if form.is_valid():  # Check if the form is valid
            with transaction.atomic():
                student_answer = form.save(commit=False)  # Save the student's answer to the current question without committing to the database
                student_answer.student = student  # Associate the student with the answer
                student_answer.question = question
                student_answer.save()  # Save the answer to the database

                if student.get_unanswered_questions(quiz).exists():  # If there are more unanswered questions
                    return redirect('take_quiz', pk)  # Redirect to the same quiz page to answer the next question
                else:
                    takenquiz = TakenQuiz.objects.create(student=student, quiz=quiz,is_checked=is_checked)
                    performance = takenquiz.calculate_score_and_percentage()
                    student.update_score()

                    return redirect('student_quiz_results', pk)  # Redirect to the student's quiz results page
    else:
        if question.question_type == "quiz":
          form = TakeQuizForm(question=question)  # Create a form instance with the current question for GET requests
        else:
          form = TakeJustificationForm(question=question)

    return render(request, 'student/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress,
        'answered_questions': total_questions - total_unanswered_questions,
        'total_questions': total_questions
    })  # Render the quiz form template, passing relevant variables and data to be displayed in the template

from django.shortcuts import render, get_object_or_404
from decimal import Decimal

@group_required("student_grp",redirect_url='home')
def student_quiz_results(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    student = request.user.student
    takenquiz = get_object_or_404(TakenQuiz, quiz=quiz, student=student)

    if takenquiz.is_checked:
        # Get student labels and scores for the chart
        student_labels = [f"{takenquiz.student.user.username} Score", "Average Score"]
        student_scores = [takenquiz.score, float(quiz.avg_score)]

        context = {
            'quiz': quiz,
            'takenquiz': takenquiz,
            'student_labels': student_labels,
            'student_scores': student_scores,
        }
        return render(request, 'student/quiz_result.html', context)
    else:
      context = {
            'quiz': quiz,
        }
      return render(request, 'student/quiz_result.html', context)
