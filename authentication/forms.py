from django import forms

class SetPasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}))

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
        

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Hashkeys

class UserRegistrationForm(UserCreationForm):
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    def __init__(self, *args, **kwargs):
        username = kwargs.pop('username', None)
        password1 = kwargs.pop('password1', None)
        super().__init__(*args, **kwargs)

        if username and password1:
            self.username = Hashkeys.decript(self.request, username)
            self.password1 = Hashkeys.decript(self.request, password1)
        else:
            self.decrypted_username = None

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

