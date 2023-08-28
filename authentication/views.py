from django.shortcuts import render,HttpResponse,redirect,reverse
from django.contrib import messages
from .decorators import group_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .models import User,Hashkeys
from .forms import SetPasswordForm

# Create your views here.'

# @group_required("Worker_grp",redirect_url='g')'
@login_required(login_url="login")
def home(request):
  if request.user.groups.filter(name__in=("admin_grp",)).exists():
    return redirect('Admin_homepage')
  elif request.user.groups.filter(name__in=("teacher_grp",)).exists():
    return redirect("teacher_home")
  elif request.user.groups.filter(name__in=("student_grp",)).exists():
    return redirect('Admin_homepage')
  else:
    return redirect("login")
    
    
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.urls import reverse

def custom_login(request):
    if request.method == 'POST':
      username = Hashkeys.decript(request,request.POST.get("username"))
      password = Hashkeys.decript(request,request.POST.get("password"))
      form = AuthenticationForm(data={"username":username,"password":password});
      if form.is_valid():
          user = authenticate(request, username=username, password=password)
          if user is not None:
              login(request, user)
              return redirect(reverse('home'))
      else:
        public_key = Hashkeys.create_hash(request)
        form.add_error(None, "Invalid username or password.")  # Add an error to the form
    
    else:
        public_key = Hashkeys.create_hash(request)
        form = AuthenticationForm(request)
    return render(request, 'login.html', {'form': form,"key":public_key})


from django.contrib.auth.models import Group
from django.db import transaction
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm
from teacher.models import Student

@transaction.atomic
def register(request):
    if request.method == 'POST':
        encrypted_username = request.POST.get('username')
        encrypted_password1 = request.POST.get('password1')
        encrypted_password2 = request.POST.get('password2')
        
        username = Hashkeys.decript(request, encrypted_username)
        password1 = Hashkeys.decript(request, encrypted_password1)
        password2 = Hashkeys.decript(request, encrypted_password2)
        
        form = UserRegistrationForm(data={'username': username, 'password1': password1, 'password2': password2})
        
        if form.is_valid():
            user = form.save()
            user = authenticate(request, username=username, password=password1)
            login(request, user)
            student = Student.objects.create(user=user)
            group = Group.objects.get(name='student_grp')  # Replace with the actual group name
            user.groups.add(group)
            return redirect('home')  # Replace with your home page URL name
        public_key = Hashkeys.create_hash(request)
    else:
        public_key = Hashkeys.create_hash(request)
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form, 'key': public_key})

#for teacher email password 
def set_password(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return redirect('home')  # Assuming 'home' is the name of the URL pattern for the home page

    if user.password:
        return redirect('home')  # If password already exists, redirect to the home page

    if request.method == 'POST':
        password1 = Hashkeys.decript(request,request.POST.get("password1"))
        password2 = Hashkeys.decript(request,request.POST.get("password2"))
        form = SetPasswordForm(data={"password1":password1,"password2":password2})
        if form.is_valid():
            password = form.cleaned_data['password1']
            user.set_password(password)
            user.save()
            authenticated_user = authenticate(username=user.username, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)

            return redirect('home')
        public_key = Hashkeys.create_hash(request)
    else:
        public_key = Hashkeys.create_hash(request)
        form = SetPasswordForm()

    return render(request, 'set_passwor.html', {'form': form,"key":public_key})


from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to the desired URL after logout
