from django import forms
from authentication.models import ClassModel,SubjectModel
from teacher.models import Quiz
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ClassModelForm(forms.ModelForm):
    class Meta:
        model = ClassModel
        fields = ['name']
        

class QuizModelForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['name']
        
class SubjectModelForm(forms.ModelForm):
    class Meta:
        model = SubjectModel
        fields = ['name', 'teacher']
        labels = {
            'name': 'Name',
            'teacher': 'Teacher',
        }

class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
