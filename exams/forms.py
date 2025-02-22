from django import forms
from django.contrib.auth.models import User
from models import Student


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'email']
