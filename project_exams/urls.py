from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

from exams import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('exams.urls')),  # This will include your app's URLs
    path('create-exam/', views.create_exam, name='create_exam'),
    path('test/', lambda request: render(request, 'test.html')),

]
