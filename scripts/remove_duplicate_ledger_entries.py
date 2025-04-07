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


if __name__ == "__main__":
    remove_duplicate_ledger_entries()
    remove_duplicate_ledger_entries()
