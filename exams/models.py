from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms


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
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    grade = models.IntegerField(choices=Student.GRADE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} - Grade {self.grade}'

    def is_accessible_to_student(self, student):
        return self.grade == student.grade and self.teacher in student.teachers.all()


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'description', 'grade', 'subject']


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
            # Create or update the student ledger entry when the score is set
            StudentLedger.objects.create(
                student=self.student,
                exam=self.question.exam,
                subject=self.question.exam.subject,
                date=self.created_at,
                score=self.score,
                teacher_name=self.question.exam.teacher.user.username,
            )


class ExamResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)  # Total score for the exam

    def __str__(self):
        return f"{self.student.user.username} - {self.exam.title}: {self.total_score}"


class StudentLedger(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    date = models.DateTimeField()
    score = models.IntegerField()  # Score of the exam
    teacher_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.student.user.username} - {self.subject} - {self.score}"
