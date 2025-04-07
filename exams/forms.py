from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, AuthenticationForm
from .models import Student, Teacher, Exam, Question, StudentAnswer


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username',
        'id': 'id_username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
        'id': 'id_password'
    }))


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
        fields = ['title', 'subject', 'description', 'grade']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'correct_answer', 'answer_choices']


class StudentForm(forms.ModelForm):
    teachers = forms.ModelMultipleChoiceField(queryset=Teacher.objects.all(), required=False,
                                              widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Student
        fields = ['grade', 'teachers']


class StudentAnswerForm(forms.ModelForm):
    class Meta:
        model = StudentAnswer
        fields = ['answer']


class GradeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        student_answers = kwargs.pop('student_answers', None)
        super(GradeForm, self).__init__(*args, **kwargs)
        if student_answers:
            for answer in student_answers:
                self.fields[f'score_{answer.id}'] = forms.IntegerField(
                    label=f'Score for {answer.student.user.username} - {answer.question.question_text}',
                    min_value=0,
                    max_value=100,
                    initial=answer.score
                )
