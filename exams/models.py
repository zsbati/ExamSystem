from django.contrib.auth.models import User
from django.db import models


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username


class Student(models.Model):
    GRADE_CHOICES = [
        (10, '10th Grade'),
        (11, '11th Grade'),
        (12, '12th Grade'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    grade = models.IntegerField(choices=GRADE_CHOICES)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.username} - Grade {self.grade}"
