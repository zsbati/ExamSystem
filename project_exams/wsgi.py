"""
WSGI config for exams project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_exams.settings')

application = get_wsgi_application() 