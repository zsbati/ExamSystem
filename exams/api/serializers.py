from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Student, Teacher, Exam, Question, StudentAnswer, ExamResult, StudentLedger

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    teachers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'user', 'grade', 'teachers', 'created_at', 'updated_at']

class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'created_at', 'updated_at']

class ExamSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)
    questions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'title', 'subject', 'teacher', 'questions', 'created_at', 'updated_at']

class QuestionSerializer(serializers.ModelSerializer):
    exam = ExamSerializer(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'exam', 'text', 'options', 'correct_answer', 'created_at', 'updated_at']

class StudentAnswerSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = StudentAnswer
        fields = ['id', 'student', 'question', 'answer', 'created_at', 'updated_at']

class ExamResultSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    exam = ExamSerializer(read_only=True)

    class Meta:
        model = ExamResult
        fields = ['id', 'student', 'exam', 'total_score', 'created_at', 'updated_at']

class StudentLedgerSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    exam = ExamSerializer(read_only=True)

    class Meta:
        model = StudentLedger
        fields = ['id', 'student', 'exam', 'subject', 'date', 'score', 'teacher_name', 'created_at', 'updated_at']
