from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import modelformset_factory
from .forms import StudentCreationForm, TeacherCreationForm, ChangeUserPasswordForm, ExamForm, QuestionForm, StudentForm
from .forms import LoginForm, StudentAnswerForm, GradeForm
from .models import Student, Teacher, Exam, Question, StudentAnswer, ExamResult
import logging

logger = logging.getLogger(__name__)


def superuser_or_teacher_required(view_func):
    @user_passes_test(lambda u: u.is_superuser or hasattr(u, 'teacher'))
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            if user.is_superuser:
                return redirect('home')
            elif hasattr(user, 'teacher'):
                return redirect('teacher_homepage')
            elif hasattr(user, 'student'):
                return redirect('student_homepage')
            else:
                messages.error(request, 'Invalid user type.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def home(request):
    context = {}
    if request.user.is_superuser:
        context = get_superuser_context(request)
        return render(request, 'dashboard.html', context)
    elif hasattr(request.user, 'teacher'):
        return redirect('teacher_homepage')
    elif hasattr(request.user, 'student'):
        return redirect('student_homepage')
    return render(request, 'home.html', context)


def get_superuser_context(request):
    search_query = request.GET.get('search', '')
    grade_filter = request.GET.get('grade', '')
    teacher_filter = request.GET.get('teacher', '')
    students = Student.objects.select_related('user').order_by('user__username')
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
    student_paginator = Paginator(students, 10)
    teacher_paginator = Paginator(teachers, 10)
    student_page = request.GET.get('student_page', 1)
    teacher_page = request.GET.get('teacher_page', 1)
    return {
        'students': student_paginator.get_page(student_page),
        'teachers': teacher_paginator.get_page(teacher_page),
        'grades': dict(Student.GRADE_CHOICES),
        'all_teachers': Teacher.objects.all(),
        'search_query': search_query,
        'grade_filter': grade_filter,
        'teacher_filter': teacher_filter,
    }


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
    students = Student.objects.all().select_related('user').order_by('grade', 'user__username')
    return render(request, 'exams/student/student_list.html', {'students': students})


@user_passes_test(is_superuser)
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    user = student.user
    if request.method == 'POST':
        student.delete()
        user.delete()
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
    next_url = request.GET.get('next', 'home')
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect(next_url)  # redirect to what was in "next"
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'exams/change_own_password.html', {
        'form': form
    })


@superuser_or_teacher_required
@login_required
def create_exam(request):
    if request.method == 'POST':
        return handle_exam_post_request(request)
    else:
        exam_form = ExamForm()
    return render(request, 'exams/create_exam.html', {'exam_form': exam_form})


def save_exam_questions(request, exam):
    question_texts = request.POST.getlist("question_text")
    correct_answers = request.POST.getlist("correct_answer")
    answer_choices_list = request.POST.getlist("answer_choices")

    logger.debug(f"Number of questions: {len(question_texts)}")

    for i in range(len(question_texts)):
        question_text = question_texts[i]
        correct_answer = correct_answers[i]
        answer_choices = answer_choices_list[i]

        logger.debug(
            f"Question {i}: {question_text}, Correct Answer: {correct_answer}, Answer Choices: {answer_choices}")

        if question_text and correct_answer and answer_choices:
            question = Question(
                exam=exam,
                question_text=question_text,
                correct_answer=correct_answer,
                answer_choices=answer_choices.split(',')
            )
            question.save()
            logger.debug(f"Saved Question {i} with ID {question.id}")
        else:
            logger.warning(
                f"Skipping Question {i} due to missing data: {question_text}, {correct_answer}, {answer_choices}")


def handle_exam_post_request(request):
    exam_form = ExamForm(request.POST)
    if exam_form.is_valid():
        exam = exam_form.save(commit=False)
        if hasattr(request.user, 'teacher'):
            exam.teacher = request.user.teacher
        else:
            messages.error(request, "You do not have an associated teacher account.")
            return redirect('create_exam')
        exam.save()
        save_exam_questions(request, exam)
        messages.success(request, 'Exam created successfully!')
        return redirect('exam_success')
    else:
        logger.error("Exam form is not valid.")
        logger.error(exam_form.errors)
        messages.error(request, 'There was an error creating the exam. Please check the form for errors.')


@login_required
def exam_success(request):
    return render(request, 'exams/exam_success.html')


@login_required
def student_homepage(request):
    if hasattr(request.user, 'student'):
        student = request.user.student
        exams = student.get_accessible_exams()
        return render(request, 'exams/student/homepage.html', {'exams': exams})
    else:
        return redirect('home')


@login_required
def teacher_homepage(request):
    return render(request, 'exams/teacher/homepage.html')


def test_template(request):
    return render(request, 'test.html')


@user_passes_test(lambda u: u.is_superuser)
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        return handle_student_post_request(request, student)
    else:
        form = StudentForm(instance=student)
    return render(request, 'exams/student/edit_student.html', {'form': form, 'student': student})


def handle_student_post_request(request, student):
    form = StudentForm(request.POST, instance=student)
    if form.is_valid():
        form.save()
        messages.success(request, 'Student updated successfully!')
        return redirect('student_list')


@user_passes_test(lambda u: u.is_superuser)
def remove_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    user = teacher.user
    try:
        teacher.delete()
        user.delete()
        messages.success(request, 'Teacher removed successfully.')
    except Exception as e:
        messages.error(request, f'An error occurred while removing the teacher: {e}')
    return redirect('dashboard')


@login_required
@superuser_or_teacher_required
def my_exams(request):
    exams = Exam.objects.filter(teacher=request.user.teacher)
    return render(request, 'exams/my_exams.html', {'exams': exams})


def exam_detail(request, exam_id):
    exam = get_exam_for_user(request, exam_id)
    context = {
        'exam': exam,
        'questions': exam.questions.all(),  # Assuming related_name is 'questions'
    }
    return render(request, 'exams/exam_detail.html', context)


def get_exam_for_user(request, exam_id):
    if request.user.is_superuser:
        return get_object_or_404(Exam, id=exam_id)
    else:
        return get_object_or_404(Exam, id=exam_id, teacher=request.user.teacher)


@login_required
@superuser_or_teacher_required
def teacher_homepage(request):
    exams = Exam.objects.filter(teacher=request.user.teacher)
    return render(request, 'exams/teacher/homepage.html', {'exams': exams})


@login_required
@superuser_or_teacher_required
def dashboard(request):
    teachers = Teacher.objects.all()
    students = Student.objects.all()

    if request.user.is_superuser:
        exams = Exam.objects.all()
        logger.debug("Superuser detected. Fetching all exams.")
    else:
        exams = Exam.objects.filter(teacher=request.user.teacher)
        logger.debug(f"Teacher detected. Fetching exams for teacher: {request.user.teacher.user.username}")

    context = {
        'teachers': teachers,
        'students': students,
        'exams': exams,
    }

    logger.debug("Rendering template: dashboard.html")
    return render(request, 'dashboard.html', context)


@login_required
@superuser_or_teacher_required
def teacher_exams(request, teacher_id):
    teacher = Teacher.objects.get(id=teacher_id)
    exams = Exam.objects.filter(teacher=teacher)

    context = {
        'teacher': teacher,
        'exams': exams,
    }

    return render(request, 'exams/teacher/teacher_exams.html', context)


@login_required
def student_exams(request):
    if hasattr(request.user, 'student'):
        student = request.user.student
        exams = student.get_accessible_exams()
        return render(request, 'exams/student_exams.html', {'exams': exams})
    else:
        return redirect('home')


@login_required
def take_exam(request, exam_id):
    if hasattr(request.user, 'student'):
        student = request.user.student
        exam = get_object_or_404(Exam, id=exam_id, grade=student.grade, teacher__in=student.teachers.all())

        # Check if the student has already taken the exam
        if StudentAnswer.objects.filter(student=student, question__exam=exam).exists():
            return redirect('exam_already_taken')

        # Create a formset for the student's answers
        StudentAnswerFormSet = modelformset_factory(StudentAnswer, form=StudentAnswerForm,
                                                    extra=len(exam.questions.all()), can_delete=False)

        if request.method == 'POST':
            formset = StudentAnswerFormSet(request.POST)
            if formset.is_valid():
                for form, question in zip(formset, exam.questions.all()):
                    answer = form.save(commit=False)
                    answer.student = student
                    answer.question = question
                    answer.save()
                return redirect('exam_submitted')
        else:
            questions = exam.questions.all()

            # Debug: Print questions
            for question in questions:
                print(f"Question: {question.question_text}")

            initial_data = [{'question': q.id, 'student': student.id} for q in questions]
            print(f"Initial Data: {initial_data}")
            formset = StudentAnswerFormSet(queryset=StudentAnswer.objects.none(), initial=initial_data)

            # Debug: Print formset data
            for form in formset:
                print(f"Form: {form.initial}")

        # Debug: Print context variables
        print(f"Context - Exam: {exam}")
        print(f"Context - Formset: {formset.management_form}")
        print(f"Context - Questions: {questions}")

        return render(request, 'exams/student/take_exam.html', {
            'exam': exam,
            'formset': formset,
            'questions': questions
        })
    else:
        return redirect('home')


@login_required
def exam_submitted(request):
    return render(request, 'exams/student/exam_submitted.html')


@login_required
def exam_already_taken(request):
    return render(request, 'exams/student/exam_already_taken.html')


@login_required
@user_passes_test(lambda u: hasattr(u, 'teacher'))
def view_student_answers(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user.teacher)
    student_answers = StudentAnswer.objects.filter(question__exam=exam).select_related('student')
    return render(request, 'exams/view_student_answers.html', {'exam': exam, 'student_answers': student_answers})


@login_required
@user_passes_test(lambda u: hasattr(u, 'teacher'))
def grade_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user.teacher)
    student_answers = StudentAnswer.objects.filter(question__exam=exam).select_related('student')
    if request.method == 'POST':
        form = GradeForm(request.POST, student_answers=student_answers)
        if form.is_valid():
            total_grades = {}
            # Save grades
            for answer in student_answers:
                grade = form.cleaned_data.get(f'grade_{answer.id}')
                answer.grade = grade
                answer.save()
                if answer.student.id not in total_grades:
                    total_grades[answer.student.id] = 0
                total_grades[answer.student.id] += grade

            # Save total grades in ExamResult
            for student_id, total_grade in total_grades.items():
                student = get_object_or_404(Student, id=student_id)
                exam_result, created = ExamResult.objects.get_or_create(student=student, exam=exam)
                exam_result.total_grade = total_grade
                exam_result.save()

            messages.success(request, 'Grades saved successfully!')
            return redirect('view_student_answers', exam_id=exam.id)
    else:
        form = GradeForm(student_answers=student_answers)
    return render(request, 'exams/grade_exam.html', {'exam': exam, 'student_answers': student_answers, 'form': form})


@login_required
def student_homepage(request):
    if hasattr(request.user, 'student'):
        student = request.user.student
        exams = student.get_accessible_exams()
        exam_results = ExamResult.objects.filter(student=student)
        return render(request, 'exams/student/homepage.html', {'exams': exams, 'exam_results': exam_results})
    else:
        return redirect('home')
