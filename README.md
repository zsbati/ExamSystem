# Exam System

A web-based exam system built with Django that allows superusers to manage students and teachers, and enables teachers
to create and administer tests for their associated students.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **User Management**:
    - Superusers can add and delete students and teachers.
    - Superusers can associate students with teachers and disassociate them as needed. Superuser accesses the student list, can add and remove teachers, via checkboxes
    - Superusers can view student grades. The student list has a 'ledger' button, that displays all the student's exams, scores. 

- **Exam Management**:
    - Teachers can create tests/exams that are accessible to students associated with them.
    - Exams can be tailored for specific grades (e.g., tenth grade).
    - Teachers can grade and re-grade exams.

- **Access Control**:
    - Only students associated with a particular teacher can access the exams created by that teacher.

## Technologies Used

- Python
- Django
- SQLite
- HTML/CSS for front-end design
- JavaScript

## Installation

Download the package on your server.

1. Create a virtual environment: python -m venv venv
   source venv/bin/activate # On Windows use `venv\Scripts\activate` (optional, but recommended)
2. Install the required packages: pip install -r requirements.txt
3. Set up the database: python manage.py migrate or: python manage.py init_db
4. Create a superuser: python manage.py createsuperuser
5. Run the code: python manage.py runserver

