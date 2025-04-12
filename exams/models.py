from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms
from django.utils import timezone


# from .models import Exam


class TeacherManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class Teacher(models.Model):
    objects = TeacherManager()
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_teacher_for_superuser(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        Teacher.objects.create(user=instance)
        print(f"Teacher instance created for superuser: {instance.username}")


class Student(models.Model):
    objects = None
    GRADE_CHOICES = [
        (10, '10th Grade'),
        (11, '11th Grade'),
        (12, '12th Grade'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    grade = models.IntegerField(choices=GRADE_CHOICES)
    teachers = models.ManyToManyField(Teacher, blank=True)

    def __str__(self):
        return f"{self.user.username} - Grade {self.grade}"

    def get_accessible_exams(self):
        return Exam.objects.filter(grade=self.grade, teacher__in=self.teachers.all())


class Exam(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    grade = models.IntegerField(choices=Student.GRADE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_timed = models.BooleanField(default=False)
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    duration_hours = models.IntegerField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.title} - Grade {self.grade}'

    def is_accessible_to_student(self, student):
        if not self.grade == student.grade or self.teacher not in student.teachers.all():
            return False
            
        if not self.is_timed:
            return True
            
        current_time = timezone.now()
        if self.start_datetime and current_time < self.start_datetime:
            return False
        if self.end_datetime and current_time > self.end_datetime:
            return False
        return True

    def get_duration_minutes(self):
        if not self.is_timed:
            return None
        return (self.duration_hours or 0) * 60 + (self.duration_minutes or 0)


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'description', 'grade', 'subject', 'is_timed', 'start_datetime', 'end_datetime', 'duration_hours', 'duration_minutes']
        widgets = {
            'is_timed': forms.CheckboxInput(attrs={'onchange': 'toggleTimingOptions(this)'}),
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'duration_hours': forms.NumberInput(attrs={'min': '0', 'max': '24'}),
            'duration_minutes': forms.NumberInput(attrs={'min': '0', 'max': '59'})
        }


class Question(models.Model):
    exam = models.ForeignKey(Exam, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    correct_answer = models.CharField(max_length=200)
    answer_choices = models.JSONField()  # To store multiple choices as a JSON array

    def __str__(self):
        return self.question_text


class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=200)
    score = models.IntegerField(null=True, blank=True)  # Score for the answer
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.question.question_text}: {self.answer}"


def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    if self.score is not None:
        # Check if a ledger entry already exists
        ledger_entry, created = StudentLedger.objects.get_or_create(
            student=self.student,
            exam=self.question.exam,
            defaults={
                'subject': self.question.exam.subject,
                'date': self.created_at,
                'score': self.score,
                'teacher_name': self.question.exam.teacher.user.username,
            }
        )
        if not created:
            # Update the existing ledger entry
            ledger_entry.score = self.score
            ledger_entry.date = self.created_at
            ledger_entry.teacher_name = self.question.exam.teacher.user.username
            ledger_entry.save()


class ExamResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)  # Total score for the exam

    def __str__(self):
        return f"{self.student.user.username} - {self.exam.title}: {self.total_score}"


class StudentLedger(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE,
        related_name='ledger_entries')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    date = models.DateTimeField()
    score = models.IntegerField()  # Score of the exam
    teacher_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('student', 'exam')

    def __str__(self):
        return f"{self.student.user.username} - {self.subject} - {self.score}"
