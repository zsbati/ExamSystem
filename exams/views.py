from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')  # Create this view later
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

def home(request):
    return render(request, 'base.html')  # or whatever template you want to use 

def logout_view(request):
    logout(request)
    return redirect('login') 