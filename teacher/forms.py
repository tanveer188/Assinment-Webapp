from django import forms
from .models import StudentJustificationAnswer

class ScoreForm(forms.ModelForm):
    class Meta:
        model = StudentJustificationAnswer
        fields = ['score']