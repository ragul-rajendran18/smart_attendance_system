from django.urls import path

from .views import (
    create_student,
    create_staff,
    login,
    student_profile,
    staff_profile,
    staff_dashboard,
    staff_classes,
    class_subjects,
    start_session,
    save_attendance,
    student_attendance,
    create_subject,
    create_batch,
    list_batches,
)
from .report_generation.weekly import weekly_report, weekly_report_excel

urlpatterns = [

    path("create-student/",create_student),
    path("create-staff/",create_staff),
    path("create-subject/",create_subject),
    path("create-batch/",create_batch),
    path("batches/",list_batches),
    path("weekly-report/",weekly_report),
    path("weekly-report/excel/",weekly_report_excel),
    path("login/", login),
    path("student/profile/", student_profile),
    path("staff/profile/", staff_profile),
    path("staff/dashboard/", staff_dashboard),
    path("staff/classes/", staff_classes),
    path("staff/class-subjects/", class_subjects),
    path("staff/start-session/", start_session),
    path("staff/save-attendance/", save_attendance),
    path("student/attendance/", student_attendance),

     

]