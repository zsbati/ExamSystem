# Generated by Django 5.1.6 on 2025-03-05 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0002_exam_question'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='teacher',
        ),
        migrations.AddField(
            model_name='student',
            name='teachers',
            field=models.ManyToManyField(blank=True, to='exams.teacher'),
        ),
    ]
