from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Student, Teacher

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email')
    search_fields = ('user__username', 'user__email')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'grade', 'teacher', 'get_email')
    list_filter = ('grade', 'teacher')
    search_fields = ('user__username', 'user__email')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student, StudentAdmin)
