from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'teachers', views.TeacherViewSet)
router.register(r'exams', views.ExamViewSet)
router.register(r'questions', views.QuestionViewSet)
router.register(r'student-answers', views.StudentAnswerViewSet)
router.register(r'exam-results', views.ExamResultViewSet)
router.register(r'student-ledger', views.StudentLedgerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
