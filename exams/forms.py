from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from .models import Student, Teacher


class TeacherCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Teacher.objects.create(user=user)
        return user


class StudentCreationForm(UserCreationForm):
    grade = forms.ChoiceField(choices=Student.GRADE_CHOICES)
    teacher = forms.ModelChoiceField(queryset=Teacher.objects.all())

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                grade=self.cleaned_data['grade'],
                teacher=self.cleaned_data['teacher']
            )
        return user


class ChangeUserPasswordForm(SetPasswordForm):
    """Form for changing user password without requiring old password"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = 'Enter the new password.'
        self.fields['new_password2'].help_text = 'Enter the same password again for verification.'
