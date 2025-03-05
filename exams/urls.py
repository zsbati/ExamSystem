from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import edit_student  # Add this import

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
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
]
