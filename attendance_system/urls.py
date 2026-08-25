from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    login,
    me,
    logout,
    admin_dashboard,
    create_student,
    student_profile,
    student_attendance,
    student_list,
    update_student,
    delete_student,
    bulk_upload_students,
    download_student_import_result,
    create_staff,
    staff_profile,
    staff_dashboard,
    staff_list,
    update_staff,
    delete_staff,
    session_list,
    session_attendance,
    create_subject,
    subject_list,
    update_subject,
    delete_subject,
    create_batch,
    list_batches,
    staff_classes,
    class_subjects,
    start_session,
    save_attendance,
    bulk_upload_staff,
    download_staff_import_result,
)
from .report_generation.weekly import weekly_report, weekly_report_excel

urlpatterns = [
    # ── Auth ──
    path("login/",                  login),
    path("logout/",                 logout),
    path("me/",                     me),
    path("token/refresh",          TokenRefreshView.as_view()),
    # ── Admin dashboard ──
    path("admin/dashboard/",        admin_dashboard),

    # ── Students ──
    path("create-student/",         create_student),
    path("student-list/",           student_list),
    path("update-student/",         update_student),
    path("delete-student/",         delete_student),
    path("student/profile/",        student_profile),
    path("student/attendance/",     student_attendance),
    path("students/bulk-upload/",   bulk_upload_students,           name="bulk-upload-students"),
    path("students/bulk-upload/download/<str:token>/", download_student_import_result, name="download-student-import-result"),

    # ── Staff ──
    path("create-staff/",           create_staff),
    path("staff-list/",             staff_list),
    path("update-staff/",           update_staff),
    path("delete-staff/",           delete_staff),
    path("staff/profile/",          staff_profile),
    path("staff/dashboard/",        staff_dashboard),
    path("staff/session-list/",     session_list),
    path("staff/session-attendance/", session_attendance),
    path("staff/classes/",          staff_classes),
    path("staff/class-subjects/",   class_subjects),
    path("staff/start-session/",    start_session),
    path("staff/save-attendance/",  save_attendance),
    path("staff/bulk-upload/",      bulk_upload_staff,              name="bulk-upload-staff"),
    path("staff/bulk-upload/download/<str:token>/", download_staff_import_result, name="download-staff-import-result"),

    # ── Subjects ──
    path("create-subject/",         create_subject),
    path("subject-list/",           subject_list),
    path("update-subject/",         update_subject),
    path("delete-subject/",         delete_subject),

    # ── Batches ──
    path("create-batch/",           create_batch),
    path("batches/",                list_batches),

    # ── Reports ──
    path("weekly-report/",          weekly_report),
    path("weekly-report/excel/",    weekly_report_excel),
    
]
