from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import StudentCreationForm, TeacherCreationForm, ChangeUserPasswordForm, ExamForm, QuestionForm
from .models import Student, Teacher, Exam, Question

def superuser_or_teacher_required(view_func):
    @user_passes_test(lambda u: u.is_superuser or hasattr(u, 'teacher'))
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            print(f"User {user.username} logged in.")  # Debugging statement
            if user.is_superuser:
                print("Redirecting to admin home.")  # Debugging statement
                return redirect('home')  # Redirect to admin home
            else:
                print("Redirecting to teacher homepage.")  # Debugging statement
                return redirect('teacher_homepage')  # Redirect to teacher homepage
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')
@login_required
def home(request):
    context = {}
    
    if request.user.is_superuser:
        # Get search parameters
        search_query = request.GET.get('search', '')
        grade_filter = request.GET.get('grade', '')
        teacher_filter = request.GET.get('teacher', '')
        
        # Query students with filters
        students = Student.objects.select_related('user', 'teacher').order_by('user__username')
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
        
        # Pagination
        student_paginator = Paginator(students, 10)  # 10 students per page
        teacher_paginator = Paginator(teachers, 10)  # 10 teachers per page
        
        student_page = request.GET.get('student_page', 1)
        teacher_page = request.GET.get('teacher_page', 1)
        
        context['students'] = student_paginator.get_page(student_page)
        context['teachers'] = teacher_paginator.get_page(teacher_page)
        context['grades'] = dict(Student.GRADE_CHOICES)
        context['all_teachers'] = Teacher.objects.all()
        context['search_query'] = search_query
        context['grade_filter'] = grade_filter
        context['teacher_filter'] = teacher_filter
        
        return render(request, 'exams/dashboard.html', context)
    
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
    students = Student.objects.all().select_related('user', 'teacher').order_by('grade', 'user__username')
    return render(request, 'exams/student/student_list.html', {'students': students})

@user_passes_test(is_superuser)
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    user = student.user
    if request.method == 'POST':
        student.delete()  # This will delete the Student instance
        user.delete()    # This will delete the associated User instance
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
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session with the new password hash so the user doesn't get logged out
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'exams/change_own_password.html', {'form': form})

from django.shortcuts import render, redirect
from .forms import ExamForm, QuestionForm
from .models import Exam, Question

@superuser_or_teacher_required
@login_required
def create_exam(request):
    print(f"Create exam accessed by: {request.user.username}")
    if request.method == 'POST':
        exam_form = ExamForm(request.POST)
        print(f"Exam form valid: {exam_form.is_valid()}")
        if exam_form.is_valid():
            exam = exam_form.save(commit=False)

            # Check if the user has a Teacher instance
            if hasattr(request.user, 'teacher'):
                exam.teacher = request.user.teacher  # Link the exam to the teacher
            else:
                # If the user is a superuser, you might want to handle it differently
                print("No teacher instance found for this user.")  # Debugging statement
                messages.error(request, "You do not have an associated teacher account.")
                return redirect('dashboard')  # Redirect to the dashboard or another appropriate view

            exam.save()
            # Save the questions
            question_count = len(request.POST.getlist('question_text_0'))
            for i in range(question_count):
                question_text = request.POST.get(f'question_text_{i}')
                correct_answer = request.POST.get(f'correct_answer_{i}')
                answer_choices = request.POST.get(f'answer_choices_{i}')
                question = Question(
                    exam=exam,
                    question_text=question_text,
                    correct_answer=correct_answer,
                    answer_choices=answer_choices.split(',')  # Assuming choices are comma-separated
                )
                question.save()
            return redirect('teacher_list')  # Redirect to the teacher list or exam list
    else:
        exam_form = ExamForm()
    return render(request, 'exams/create_exam.html', {'exam_form': exam_form})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def teacher_homepage(request):
    return render(request, 'exams/teacher/homepage.html')

@login_required
def dashboard(request):
    context = {
        'teachers': Teacher.objects.all(),
        'students': Student.objects.all(),
    }
    return render(request, 'exams/dashboard.html', context)