from django.contrib.auth.models import User
from django.db import models


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
