import os
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_exams.settings')

# Import Django models after configuring the environment
import django

django.setup()

from exams.models import StudentLedger


def remove_duplicate_ledger_entries():
    seen = set()
    duplicates = []

    for ledger in StudentLedger.objects.all():
        key = (ledger.student_id, ledger.exam_id)
        if key in seen:
            duplicates.append(ledger.id)
        else:
            seen.add(key)

    # Delete duplicates
    StudentLedger.objects.filter(id__in=duplicates).delete()
    print(f"Deleted {len(duplicates)} duplicate entries.")


if __name__ == "__main__":
    remove_duplicate_ledger_entries()
