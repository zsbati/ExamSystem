from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from .models import Student, Teacher, Exam, Question


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
    teachers = forms.ModelMultipleChoiceField(queryset=Teacher.objects.all(), required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            student = Student.objects.create(
                user=user,
                grade=self.cleaned_data['grade']
            )
            student.teachers.set(self.cleaned_data['teachers'])
        return user


class ChangeUserPasswordForm(SetPasswordForm):
    """Form for changing user password without requiring old password"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = 'Enter the new password.'
        self.fields['new_password2'].help_text = 'Enter the same password again for verification.'


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'description', 'grade']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'correct_answer', 'answer_choices']
