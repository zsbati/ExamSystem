from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Student, Teacher
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages


class TeacherInline(admin.TabularInline):
    model = Student.teachers.through
    extra = 1


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email')
    search_fields = ('user__username', 'user__email')

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = 'Email'


class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'grade', 'get_teachers', 'get_email')
    list_filter = ('grade',)
    search_fields = ('user__username', 'user__email')
    inlines = [TeacherInline]

    def get_teachers(self, obj):
        return ", ".join([teacher.user.username for teacher in obj.teachers.all()])

    get_teachers.short_description = 'Teachers'

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = 'Email'

    get_email.short_description = 'Email'


admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher)



