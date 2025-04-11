from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from ..models import Student, Teacher, Exam, Question, StudentAnswer, ExamResult, StudentLedger
from .serializers import (
    UserSerializer, StudentSerializer, TeacherSerializer,
    ExamSerializer, QuestionSerializer, StudentAnswerSerializer,
    ExamResultSerializer, StudentLedgerSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Student.objects.all()
        elif hasattr(user, 'teacher'):
            return Student.objects.filter(teachers=user.teacher)
        return Student.objects.filter(user=user)

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAdminUser]

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Exam.objects.all()
        elif hasattr(user, 'teacher'):
            return Exam.objects.filter(teacher=user.teacher)
        return Exam.objects.filter(student__user=user)

    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        exam = self.get_object()
        serializer = QuestionSerializer(exam.questions.all(), many=True)
        return Response(serializer.data)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Question.objects.all()
        elif hasattr(user, 'teacher'):
            return Question.objects.filter(exam__teacher=user.teacher)
        return Question.objects.filter(exam__student__user=user)

class StudentAnswerViewSet(viewsets.ModelViewSet):
    queryset = StudentAnswer.objects.all()
    serializer_class = StudentAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return StudentAnswer.objects.all()
        elif hasattr(user, 'teacher'):
            return StudentAnswer.objects.filter(question__exam__teacher=user.teacher)
        return StudentAnswer.objects.filter(student__user=user)

class ExamResultViewSet(viewsets.ModelViewSet):
    queryset = ExamResult.objects.all()
    serializer_class = ExamResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ExamResult.objects.all()
        elif hasattr(user, 'teacher'):
            return ExamResult.objects.filter(exam__teacher=user.teacher)
        return ExamResult.objects.filter(student__user=user)

class StudentLedgerViewSet(viewsets.ModelViewSet):
    queryset = StudentLedger.objects.all()
    serializer_class = StudentLedgerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return StudentLedger.objects.all()
        elif hasattr(user, 'teacher'):
            return StudentLedger.objects.filter(student__teachers=user.teacher)
        return StudentLedger.objects.filter(student__user=user)
