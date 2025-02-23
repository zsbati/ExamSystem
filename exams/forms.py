from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Student, Teacher


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
