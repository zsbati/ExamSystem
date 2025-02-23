from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .forms import StudentCreationForm
from .models import Student

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

def home(request):
    return render(request, 'base.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def create_student(request):
    if request.method == 'POST':
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student account created successfully!')
            return redirect('student_list')
    else:
        form = StudentCreationForm()
    
    return render(request, 'student/create_student.html', {'form': form})

@user_passes_test(is_superuser)
def student_list(request):
    students = Student.objects.all().select_related('user', 'teacher')
    return render(request, 'student/student_list.html', {'students': students})