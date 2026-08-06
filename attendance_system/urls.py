from django.urls import path

from .views import create_student,create_staff,login,student_profile,staff_profile,staff_dashboard,start_session

urlpatterns = [

    path("create-student/",create_student),
    path("create-staff/",create_staff),
    path("login/", login),
    path("student/profile/", student_profile),
    path("staff/profile/", staff_profile),
     path("staff/dashboard/", staff_dashboard),
     path("staff/start-session/", start_session),
]