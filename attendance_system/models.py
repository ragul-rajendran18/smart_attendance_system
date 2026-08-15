from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    ROLE_CHOICES = (
        ('ADMIN', 'ADMIN'),
        ('STAFF', 'STAFF'),
        ('STUDENT', 'STUDENT'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username

class Student(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_name = models.CharField(max_length=100)
    register_no = models.CharField(max_length=20, unique=True)
    class_name = models.CharField(max_length=50)

    def __str__(self):
        return self.student_name

class Staff(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_name = models.CharField(max_length=100)
    staff_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.staff_name

# -------------------------
# Subject Model
# -------------------------

class Subject(models.Model):

    subject_code = models.CharField(max_length=20, unique=True)

    subject_name = models.CharField(max_length=100)

    class_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.class_name} - {self.subject_name}"


# -------------------------
# Staff Subject Mapping
# -------------------------

class StaffSubject(models.Model):

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE
    )

    class_name = models.CharField(max_length=50)

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.staff.staff_name} - {self.class_name} - {self.subject.subject_name}"


# -------------------------
# Time Table
# -------------------------

class TimeTable(models.Model):

    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    )

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE
    )

    class_name = models.CharField(max_length=50)

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    day = models.CharField(
        max_length=20,
        choices=DAY_CHOICES
    )

    period = models.PositiveIntegerField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    def __str__(self):
        return f"{self.day} - P{self.period} - {self.class_name}"


# -------------------------
# Attendance Session
# -------------------------

class AttendanceSession(models.Model):

    STATUS_CHOICES = (
        ('ACTIVE', 'ACTIVE'),
        ('COMPLETED', 'COMPLETED'),
    )

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE
    )

    class_name = models.CharField(max_length=50)

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    date = models.DateField()

    period = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    def __str__(self):
        return f"{self.date} - {self.class_name} - Period {self.period}"


# -------------------------
# Attendance
# -------------------------

class Attendance(models.Model):

    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    )

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student.student_name} - {self.status}"


class Attendance(models.Model):

    STATUS_CHOICES = (
        ("Present", "Present"),
        ("Absent", "Absent"),
    )

    session = models.ForeignKey(
        TimeTable,
        on_delete=models.CASCADE
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    def __str__(self):
        return f"{self.student.student_name} - {self.status}"    