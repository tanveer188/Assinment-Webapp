from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib.auth.models import Group,User
from django.http import JsonResponse
from django.contrib import messages
from authentication.models import ClassModel,SubjectModel,TeacherModel
from teacher.models import Quiz,Question,Answer
from authentication.decorators import group_required
from .forms import ClassModelForm,SubjectModelForm,UserRegistrationForm,QuizModelForm
import json
from django.views.decorators.csrf import csrf_exempt
from Mail.email import sendMail
from django.db import transaction
# Create your views here.

@group_required("admin_grp","student_grp",redirect_url='home')
def admin_home(request):
  classes = ClassModel.objects.all()
  context = {
    "classes":classes
  }
  return render(request,'Admin/home.html',context)

@group_required("admin_grp","student_grp",redirect_url='home')
def class_view(request,pk):
  class_name = get_object_or_404(ClassModel,pk=pk)
  subjects = SubjectModel.objects.filter(class_name=class_name)
  context = {
    "class_name":class_name,
    "subjects":subjects
  }
  return render(request,'Admin/class.html',context)

@group_required("admin_grp",redirect_url='home')
def staff_view(request):
  staffs = TeacherModel.objects.all()
  context = {
    "staffs":staffs
  }
  return render(request,"Admin/staff.html",context)


@group_required("admin_grp","student_grp",redirect_url='home')
def quiz_view(request,pk):
  subject = get_object_or_404(SubjectModel,pk=pk)
  quizzes = subject.quizzes.all()
  context = {
    "quizzes":quizzes,
    "pk":pk
  }
  return render(request,"Admin/quiz.html",context)

@group_required("admin_grp","teacher_grp",redirect_url='home')
def create_quizz(request,pk):
    subject = get_object_or_404(SubjectModel,pk=pk)
    if request.method == "POST":
        submitedform = QuizModelForm(data=request.POST)

        if submitedform.is_valid():
            instance = submitedform.save(commit=False)
            instance.subject = subject
            instance.teacher = request.user
            instance.save()
            return redirect("submit_quiz",pk=instance.id)
        else:
            form = submitedform
    else:
        form = QuizModelForm()

    context = {
      "Title":"Quiz",
        "form": form,
    }
    return render(request, "form.html", context)

from django.contrib.auth.decorators import user_passes_test


@group_required("admin_grp", "teacher_grp", redirect_url='home')
def removeQuiz(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pk = data.get('pk')
        instance = get_object_or_404(Quiz, pk=pk)
        user = request.user
        if user.groups.filter(name='admin_grp').exists():
            instance.delete()
        elif user.groups.filter(name='teacher_grp').exists() and instance.teacher == user:
            instance.delete()
        else:
          context = {"status":False}
          return JsonResponse(context)
        context = {"status": True}
        return JsonResponse(context)


@group_required("admin_grp", "teacher_grp", redirect_url='home')
def submit_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.method == 'POST':
      with transaction.atomic():
        question_list = []
        option_keys = [key for key in request.POST.keys() if key.startswith('option_')]
        
        for key, value in request.POST.items():
            if key.startswith('question_'):
                question_number = key.split('_')[1]
                question_key = f"question_{question_number}"
                if question_key not in question_list:
                    question_list.append([value, [], None])
                else:
                    question_list[-1][0] = value
            elif key.startswith('answer_'):
                question_number = key.split('_')[1]
                question_list[-1][2] = value

        for option_key in option_keys:
            question_number = option_key.split('_')[1]
            options = request.POST.getlist(option_key)
            question_list[int(question_number) - 1][1].extend(map(str, options))

        for question_data in question_list:
            question_text, options, correct_answer = question_data

            # Determine the question type based on the presence of options
            if len(options) == 0:
                question_type = 'justification'
                question = Question.objects.create(quiz=quiz, text=question_text, question_type=question_type)
            else:
                question_type = 'quiz'
                question = Question.objects.create(quiz=quiz, text=question_text, question_type=question_type)
                for i in range(len(options)):
                    if i+1 == int(correct_answer[0]):
                      is_correct =True
                    else:
                      is_correct =False
                    Answer.objects.create(question=question, text=options[i], is_correct=is_correct)

        response_data = {
            'Question': question_list
        }
        return redirect("quiz_view",pk=quiz.subject.id)

    context = {
        "quiz": quiz,
        "pk": pk,
    }
    return render(request, "Admin/setup_quiz.html", context)


@group_required("admin_grp",redirect_url='home')
def register_teacher(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name='teacher_grp')
            user.groups.add(group)
            sendMail(request,user.email,user.username,user.id)
            instance = TeacherModel()
            instance.user =user
            instance.role=request.POST.get("role")
            print(instance.role)
            instance.save()
            return redirect("staff_view")
    else:
        form = UserRegistrationForm()
    return render(request, 'Admin/form.html', {'form': form,"Title":"Teacher"})

    
@group_required("admin_grp",redirect_url='home')
def removeteacher(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pk = data.get('pk')
        instance = get_object_or_404(TeacherModel, pk=pk)
        user = instance.user
        user.delete()
        context = {"status": True}
        return JsonResponse(context)

@group_required("admin_grp",redirect_url='home')
def newclass(request):
    if request.method == "POST":
        submitedform = ClassModelForm(data=request.POST)

        if submitedform.is_valid():
            instance = submitedform.save()
            messages.success(request, "New Class Added")
            return redirect("home")
        else:
            form = submitedform
    else:
        form = ClassModelForm()

    context = {
      "Title":"Class",
        "form": form,
    }
    return render(request, "form.html", context)


@group_required("admin_grp",redirect_url='home')
def newsubject(request,pk):
    if request.method == "POST":
        class_name = get_object_or_404(ClassModel,pk=pk)
        submitedform = SubjectModelForm(data=request.POST)

        if submitedform.is_valid():
            instance = submitedform.save(commit=False)
            instance.class_name = class_name
            instance.save()
            messages.success(request, "New Class Added")
            return redirect("class_view",pk=pk)
        else:
            form = submitedform
    else:
        form = SubjectModelForm()

    context = {
      "Title":"Subject",
        "form": form,
    }
    return render(request, "form.html", context)


@group_required("admin_grp", redirect_url='home')
def Edit(request, model_name, pk):
    context = {}
    
    if model_name == "Class":
        instance = get_object_or_404(ClassModel, pk=pk)
        form = ClassModelForm(request.POST or None, instance=instance)
        
        if request.method == "POST":
            if form.is_valid():
                form.save()
                messages.success(request, "Updated Successfully")
                return redirect("home")
            else:
                context["form"] = form
                return render(request, "form.html", context)
        
        context["form"] = form
    
    elif model_name == "Subject":
        instance = get_object_or_404(SubjectModel, pk=pk)
        form = SubjectModelForm(request.POST or None, instance=instance)
        
        if request.method == "POST":
            if form.is_valid():
                form.save()
                messages.success(request, "Updated Successfully")
                return redirect("class_view",pk=instance.class_name.id)
            else:
                context["form"] = form
                return render(request, "form.html", context)
        
        context["form"] = form
    context["Title"] = model_name
    return render(request, "form.html", context)

  
@group_required("admin_grp",redirect_url='home')
def Delete_clas(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pk = data.get('pk')
        instance = get_object_or_404(ClassModel, pk=pk)
        instance.delete()
        context = {"status": True}
        return JsonResponse(context)
  
@group_required("admin_grp",redirect_url='home')
def Delete_subject(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pk = data.get('pk')
        instance = get_object_or_404(SubjectModel, pk=pk)
        instance.delete()
        context = {"status": True}
        return JsonResponse(context)
    
    

from django.urls import reverse
from django.db.models import Count
from teacher.models import WebsiteVisit

@group_required("admin_grp", redirect_url='home')
def dashboard(request):
    classes = ClassModel.objects.all()

    class_names = []
    view_counts_class = []
    class_colors = []

    for class_obj in classes:
        print(class_obj)
        url_name = request.build_absolute_uri(reverse('class_view', kwargs={'pk': class_obj.id}))
        visit_count = WebsiteVisit.objects.filter(visited_url=url_name).count()
        print(url_name)
        class_names.append(class_obj.name)
        view_counts_class.append(visit_count)
        #class_colors.append(generate_random_color())

    context = {
      "classdata":[class_names,view_counts_class],
    }

    # quizzes = Quiz.objects.all()

    # quiz_names = []
    # quiz_view_counts = []
    # quiz_colors = []

    # for quiz in quizzes:
    #     url_name = reverse('quiz_view', kwargs={'pk': quiz.id})
    #     visit_count = WebsiteVisit.objects.filter(visited_url=url_name).count()
    #     quiz_names.append(quiz.name)
    #     quiz_view_counts.append(visit_count)
    #     #quiz_colors.append(generate_random_color())

    # context['quiz_names'] = quiz_names
    # context['quiz_view_counts'] = quiz_view_counts

    return render(request, 'Admin/dashboard.html', context)
