from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_own_password, name='change_own_password'),
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.create_student, name='create_student'),
    path('students/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    path('students/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('students/<int:student_id>/change-password/', views.change_student_password, name='change_student_password'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/create/', views.create_teacher, name='create_teacher'),
    path('teachers/<int:teacher_id>/change-password/', views.change_teacher_password, name='change_teacher_password'),
    path('exams/create/', views.create_exam, name='create_exam'),
    path('teacher/homepage/', views.teacher_homepage, name='teacher_homepage'),
    path('student/homepage/', views.student_homepage, name='student_homepage'),
    path('remove_teacher/<int:teacher_id>/', views.remove_teacher, name='remove_teacher'),
    path('test/', views.test_template, name='test_template'),
    path('success/', views.exam_success, name='exam_success'),
]
