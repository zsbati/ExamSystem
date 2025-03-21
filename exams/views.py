from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import StudentCreationForm, TeacherCreationForm, ChangeUserPasswordForm, ExamForm, QuestionForm, StudentForm
from .forms import LoginForm
from .models import Student, Teacher, Exam, Question
import logging

logger = logging.getLogger(__name__)


def superuser_or_teacher_required(view_func):
    @user_passes_test(lambda u: u.is_superuser or hasattr(u, 'teacher'))
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            if user.is_superuser:
                return redirect('home')
            elif hasattr(user, 'teacher'):
                return redirect('teacher_homepage')
            elif hasattr(user, 'student'):
                return redirect('student_homepage')
            else:
                messages.error(request, 'Invalid user type.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def home(request):
    context = {}
    if request.user.is_superuser:
        search_query = request.GET.get('search', '')
        grade_filter = request.GET.get('grade', '')
        teacher_filter = request.GET.get('teacher', '')
        students = Student.objects.select_related('user').order_by('user__username')
        teachers = Teacher.objects.select_related('user').order_by('user__username')
        if search_query:
            students = students.filter(
                Q(user__username__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(teacher__user__username__icontains=search_query)
            )
            teachers = teachers.filter(
                Q(user__username__icontains=search_query) |
                Q(user__email__icontains=search_query)
            )
        if grade_filter:
            students = students.filter(grade=grade_filter)
        if teacher_filter:
            students = students.filter(teacher_id=teacher_filter)
        student_paginator = Paginator(students, 10)
        teacher_paginator = Paginator(teachers, 10)
        student_page = request.GET.get('student_page', 1)
        teacher_page = request.GET.get('teacher_page', 1)
        context['students'] = student_paginator.get_page(student_page)
        context['teachers'] = teacher_paginator.get_page(teacher_page)
        context['grades'] = dict(Student.GRADE_CHOICES)
        context['all_teachers'] = Teacher.objects.all()
        context['search_query'] = search_query
        context['grade_filter'] = grade_filter
        context['teacher_filter'] = teacher_filter
        return render(request, 'dashboard.html', context)
    return render(request, 'home.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')


def is_superuser(user):
    return user.is_superuser


@user_passes_test(is_superuser)
def create_teacher(request):
    if request.method == 'POST':
        form = TeacherCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher account created successfully!')
            return redirect('home')
    else:
        form = TeacherCreationForm()
    return render(request, 'exams/teacher/create_teacher.html', {'form': form})


@user_passes_test(is_superuser)
def teacher_list(request):
    teachers = Teacher.objects.all().select_related('user')
    return render(request, 'exams/teacher/teacher_list.html', {'teachers': teachers})


@user_passes_test(is_superuser)
def create_student(request):
    if request.method == 'POST':
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student account created successfully!')
            return redirect('home')
    else:
        form = StudentCreationForm()
    return render(request, 'exams/student/create_student.html', {'form': form})


@user_passes_test(is_superuser)
def student_list(request):
    students = Student.objects.all().select_related('user').order_by('grade', 'user__username')
    return render(request, 'exams/student/student_list.html', {'students': students})


@user_passes_test(is_superuser)
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    user = student.user
    if request.method == 'POST':
        student.delete()
        user.delete()
        messages.success(request, f'Student {user.username} has been deleted successfully.')
        return redirect('home')
    return render(request, 'exams/student/confirm_delete.html', {'student': student})


@user_passes_test(is_superuser)
def change_student_password(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = ChangeUserPasswordForm(user=student.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Password for student {student.user.username} has been changed successfully.')
            return redirect('home')
    else:
        form = ChangeUserPasswordForm(user=student.user)
    return render(request, 'exams/student/change_password.html', {
        'form': form,
        'student': student
    })


@user_passes_test(is_superuser)
def change_teacher_password(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        form = ChangeUserPasswordForm(user=teacher.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Password for teacher {teacher.user.username} has been changed successfully.')
            return redirect('home')
    else:
        form = ChangeUserPasswordForm(user=teacher.user)
    return render(request, 'exams/teacher/change_password.html', {
        'form': form,
        'teacher': teacher
    })


@login_required
def change_own_password(request):
    next_url = request.GET.get('next', 'home')
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect(next_url)  # redirect to what was in "next"
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'exams/change_own_password.html', {
        'form': form
    })


@superuser_or_teacher_required
@login_required
def create_exam(request):
    if request.method == 'POST':
        exam_form = ExamForm(request.POST)
        if exam_form.is_valid():
            exam = exam_form.save(commit=False)
            if hasattr(request.user, 'teacher'):
                exam.teacher = request.user.teacher
            else:
                messages.error(request, "You do not have an associated teacher account.")
                return redirect('create_exam')
            exam.save()
            question_count = len(request.POST.getlist('question_text_0'))
            for i in range(question_count):
                question_text = request.POST.get(f'question_text_{i}')
                correct_answer = request.POST.get(f'correct_answer_{i}')
                answer_choices = request.POST.get(f'answer_choices_{i}')
                question = Question(
                    exam=exam,
                    question_text=question_text,
                    correct_answer=correct_answer,
                    answer_choices=answer_choices.split(',')
                )
                question.save()
            messages.success(request, 'Exam created successfully!')
            return redirect('exam_success')
    else:
        exam_form = ExamForm()
    return render(request, 'exams/create_exam.html', {'exam_form': exam_form})


@login_required
def exam_success(request):
    return render(request, 'exams/exam_success.html')


@login_required
def student_homepage(request):
    # Add any necessary context or data to pass to the template
    context = {}
    return render(request, 'exams/student/homepage.html', context)


@login_required
def teacher_homepage(request):
    return render(request, 'exams/teacher/homepage.html')


def test_template(request):
    return render(request, 'test.html')


@user_passes_test(lambda u: u.is_superuser)
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'exams/student/edit_student.html', {'form': form, 'student': student})


@user_passes_test(is_superuser)
def remove_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    user = teacher.user
    teacher.delete()
    user.delete()
    messages.success(request, 'Teacher removed successfully.')
    return redirect('dashboard')


@login_required
@superuser_or_teacher_required
def my_exams(request):
    exams = Exam.objects.filter(teacher=request.user.teacher)
    return render(request, 'exams/my_exams.html', {'exams': exams})


def exam_detail(request, exam_id):
    # Superusers can view any exam
    if request.user.is_superuser:
        exam = get_object_or_404(Exam, id=exam_id)
    else:
        # Teachers can only view their own exams
        exam = get_object_or_404(Exam, id=exam_id, teacher=request.user.teacher)

    context = {
        'exam': exam,
        'questions': exam.questions.all(),  # Assuming related_name is 'questions'
    }

    return render(request, 'exams/exam_detail.html', context)


@login_required
@superuser_or_teacher_required
def teacher_homepage(request):
    exams = Exam.objects.filter(teacher=request.user.teacher)
    return render(request, 'exams/teacher/homepage.html', {'exams': exams})


@login_required
@superuser_or_teacher_required
def dashboard(request):
    teachers = Teacher.objects.all()
    students = Student.objects.all()

    if request.user.is_superuser:
        exams = Exam.objects.all()
        logger.debug("Superuser detected. Fetching all exams.")
    else:
        exams = Exam.objects.filter(teacher=request.user.teacher)
        logger.debug(f"Teacher detected. Fetching exams for teacher: {request.user.teacher.user.username}")

    context = {
        'teachers': teachers,
        'students': students,
        'exams': exams,
    }

    return render(request, 'exams/dashboard.html', context)


@login_required
@superuser_or_teacher_required
def teacher_exams(request, teacher_id):
    teacher = Teacher.objects.get(id=teacher_id)
    exams = Exam.objects.filter(teacher=teacher)

    context = {
        'teacher': teacher,
        'exams': exams,
    }

    return render(request, 'exams/teacher/teacher_exams.html', context)
