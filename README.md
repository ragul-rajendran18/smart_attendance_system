# Smart Attendance System

A **role-based web-based attendance management system** built with Django REST Framework. The system provides separate workflows for **Admin, Staff, and Students**, with timetable-based attendance tracking and automated weekly Excel reports.

## Features

### Admin

* Manage students and staff.
* Create and manage subjects and batches.
* Assign holidays and prevent attendance sessions on holidays.
* Manage academic data through role-protected APIs.
* Generate weekly attendance reports in Excel format.
* View period-wise attendance records.

### Staff

* View assigned classes and subjects.
* Start attendance sessions based on the active timetable period.
* Mark students as **Present/Absent**.
* Edit attendance during the active session period.
* View attendance-related information.
* Attendance sessions are automatically blocked on holidays.

### Student

* View profile information.
* View attendance records.
* View holiday information.
* Access attendance data based on their class and batch.

## Attendance Workflow

```text
Admin
  │
  ├── Students
  ├── Staff
  ├── Subjects
  ├── Batches
  └── Holidays
        │
        ▼
      Staff
        │
        ├── Select Class
        ├── Select Subject
        ├── Start Session
        └── Mark Attendance
                │
                ▼
          Present / Absent
                │
                ▼
             Student
                │
                └── View Attendance

Admin
  │
  └── Weekly Report
          │
          ▼
      Excel Report
```

## Weekly Report

The system generates a structured Excel report containing:

* Student name
* Register number
* Class
* Date
* Period
* Subject
* Present/Absent status

Example:

| Register No | Student Name | 17 Aug P1 DBMS | 17 Aug P2 Java | 18 Aug P1 DBMS |
| ----------- | ------------ | -------------- | -------------- | -------------- |
| 23IT101     | Ragul        | P              | P              | A              |
| 23IT102     | Arjun        | P              | A              | P              |

The report is generated dynamically from the attendance sessions and attendance records.

## Authentication & Authorization

The system uses **JWT authentication** with role-based access control.

```text
ADMIN
 ├── Student Management
 ├── Staff Management
 ├── Subject Management
 ├── Batch Management
 ├── Holiday Management
 └── Weekly Reports

STAFF
 ├── Classes
 ├── Subjects
 ├── Start Session
 ├── Mark Attendance
 └── Edit Attendance

STUDENT
 ├── Profile
 └── Attendance
```

## Technology Stack

### Backend

* Python
* Django
* Django REST Framework
* Simple JWT

### Database

* TiDB Cloud
* MySQL-compatible database
* PyMySQL

### Report Generation

* OpenPyXL
* Excel `.xlsx`

### Development & Deployment

* Docker
* Git
* GitHub
* Postman
* Render

## Project Structure

```text
smart_attendance_system/
│
├── attendance_system/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   │
│   ├── report_generation/
│   │   └── weekly.py
│   │
│   └── ...
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
│
├── manage.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## Main API Endpoints

### Authentication

```text
POST /api/login/
```

### Admin

```text
POST /api/create-student/
POST /api/create-staff/
POST /api/create-subject/
POST /api/create-batch/

GET  /api/student-list/

POST /api/holidays/create/
GET  /api/holidays/
GET  /api/holidays/today/
```

### Staff

```text
GET  /api/staff/profile/
GET  /api/staff/dashboard/
GET  /api/staff/classes/
GET  /api/staff/class-subjects/

POST /api/staff/start-session/
POST /api/staff/save-attendance/
PUT  /api/staff/edit-attendance/
```

### Student

```text
GET /api/student/profile/
GET /api/student/attendance/
```

### Reports

```text
GET /api/weekly-report/
GET /api/weekly-report/excel/
```

## Installation

Clone the repository:

```bash
git clone <your-github-repository-url>
cd smart_attendance_system
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

## Environment Variables

For deployment, keep sensitive configuration such as:

```text
SECRET_KEY
DATABASE_NAME
DATABASE_USER
DATABASE_PASSWORD
DATABASE_HOST
DATABASE_PORT
```

in environment variables rather than committing credentials to GitHub.

## Deployment

The backend can be deployed using Docker and Render.

```text
Frontend
   │
   ▼
Django REST API
   │
   ▼
TiDB Cloud
```

## Future Enhancements

* Attendance analytics dashboard.
* Low-attendance notifications.
* Automated email notifications.
* Monthly and semester-wise reports.
* Advanced attendance statistics.
* Mobile application integration.

## Author

**Ragul**
B.Tech Information Technology
Django REST Framework | Python | Backend Development
