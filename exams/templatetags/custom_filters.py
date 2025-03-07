from django import template
from exams.models import Teacher

register = template.Library()


@register.filter(name='custom_filter')
def custom_filter(value):
    return value


@register.filter
def is_teacher(user):
    return hasattr(user, 'teacher')


@register.filter
def is_superuser(user):
    return user.is_superuser
