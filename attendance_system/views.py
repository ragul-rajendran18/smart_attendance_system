from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Student, Staff
from .serializer import (
    StudentSerializer,
    StaffSerializer,
    LoginSerializer,
    TimeTableSerializer
)
from .utils import generate_username, generate_password
from datetime import datetime
from .models import TimeTable



# ============================
# Create Student
# ============================

@api_view(["POST"])
def create_student(request):

    serializer = StudentSerializer(data=request.data)

    if serializer.is_valid():

        username = generate_username("STU")
        password = generate_password()

        user = User.objects.create(
            username=username,
            password=make_password(password),
            role="STUDENT"
        )

        Student.objects.create(
            user=user,
            student_name=serializer.validated_data["student_name"],
            register_no=serializer.validated_data["register_no"],
            class_name=serializer.validated_data["class_name"]
        )

        return Response({
            "message": "Student Created Successfully",
            "username": username,
            "password": password
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================
# Create Staff
# ============================

@api_view(["POST"])
def create_staff(request):

    serializer = StaffSerializer(data=request.data)

    if serializer.is_valid():

        username = generate_username("STF")
        password = generate_password()

        user = User.objects.create(
            username=username,
            password=make_password(password),
            role="STAFF"
        )

        Staff.objects.create(
            user=user,
            staff_name=serializer.validated_data["staff_name"],
            staff_id=serializer.validated_data["staff_id"]
        )

        return Response({
            "message": "Staff Created Successfully",
            "username": username,
            "password": password
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================
# Login
# ============================

@api_view(["POST"])
def login(request):

    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {
                    "message": "Invalid Username or Password"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response({

            "message": "Login Successful",

            "role": user.role,

            "access": str(refresh.access_token),

            "refresh": str(refresh)

        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================
# Student Profile
# ============================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_profile(request):

    try:

        student = Student.objects.get(user=request.user)

        return Response({

            "student_name": student.student_name,

            "register_no": student.register_no,

            "class_name": student.class_name,

            "username": request.user.username,

            "role": request.user.role

        })

    except Student.DoesNotExist:

        return Response(
            {
                "message": "Student Profile Not Found"
            },
            status=status.HTTP_404_NOT_FOUND
        )


# ============================
# Staff Profile
# ============================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def staff_profile(request):

    try:

        staff = Staff.objects.get(user=request.user)

        return Response({

            "staff_name": staff.staff_name,

            "staff_id": staff.staff_id,

            "username": request.user.username,

            "role": request.user.role

        })

    except Staff.DoesNotExist:

        return Response(
            {
                "message": "Staff Profile Not Found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def staff_dashboard(request):

    if request.user.role != "STAFF":
        return Response(
            {
                "message": "Permission Denied"
            },
            status=403
        )

    staff = Staff.objects.get(user=request.user)

    current_day = datetime.now().strftime("%A")

    current_time = datetime.now().time()

    timetable = TimeTable.objects.filter(

        staff=staff,

        day=current_day,

        start_time__lte=current_time,

        end_time__gte=current_time

    ).first()

    if timetable is None:

        return Response({

            "message": "No Active Session"

        })

    serializer = TimeTableSerializer(timetable)

    return Response({

        "status": "LIVE",

        "session": serializer.data

    })


from datetime import datetime, time

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def staff_dashboard(request):

    if request.user.role != "STAFF":
        return Response(
            {"message": "Permission Denied"},
            status=status.HTTP_403_FORBIDDEN
        )

    current_time = datetime.now().time()

    if time(10, 0) <= current_time <= time(10, 50):
        period = 1
        start = "10:00"
        end = "10:50"

    elif time(11, 0) <= current_time <= time(11, 50):
        period = 2
        start = "11:00"
        end = "11:50"

    elif time(12, 0) <= current_time <= time(12, 50):
        period = 3
        start = "12:00"
        end = "12:50"

    elif time(13, 30) <= current_time <= time(14, 20):
        period = 4
        start = "13:30"
        end = "14:20"

    elif time(14, 20) <= current_time <= time(15, 10):
        period = 5
        start = "14:20"
        end = "15:10"

    else:
        return Response({
            "message": "No Active Session"
        })

    return Response({
        "status": "LIVE",
        "period": period,
        "start_time": start,
        "end_time": end
    })

from datetime import time
from .models import Subject

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_session(request):

    if request.user.role != "STAFF":
        return Response(
            {"message": "Permission Denied"},
            status=status.HTTP_403_FORBIDDEN
        )

    staff = Staff.objects.get(user=request.user)

    class_name = request.data.get("class_name")
    subject_id = request.data.get("subject_id")

    if not class_name or not subject_id:
        return Response(
            {"message": "class_name and subject_id are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return Response(
            {"message": "Subject Not Found"},
            status=status.HTTP_404_NOT_FOUND
        )

    current_day = datetime.now().strftime("%A")
    current_time = datetime.now().time()

    if time(10,0) <= current_time <= time(10,50):
        period = 1
        start = time(10,0)
        end = time(10,50)

    elif time(11,0) <= current_time <= time(11,50):
        period = 2
        start = time(11,0)
        end = time(11,50)

    elif time(12,0) <= current_time <= time(12,50):
        period = 3
        start = time(12,0)
        end = time(12,50)

    elif time(13,30) <= current_time <= time(14,20):
        period = 4
        start = time(13,30)
        end = time(14,20)

    elif time(14,20) <= current_time <= time(15,10):
        period = 5
        start = time(14,20)
        end = time(15,10)

    else:
        return Response(
            {"message": "No Active Session"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if TimeTable.objects.filter(
        staff=staff,
        day=current_day,
        period=period
    ).exists():

        return Response({
            "message": "Session already started."
        })

    session = TimeTable.objects.create(
        staff=staff,
        class_name=class_name,
        subject=subject,
        day=current_day,
        period=period,
        start_time=start,
        end_time=end
    )

    students = Student.objects.filter(class_name=class_name)

    data = []

    for student in students:
        data.append({
            "id": student.id,
            "student_name": student.student_name,
            "register_no": student.register_no
        })

    return Response({

        "message": "Session Started Successfully",

        "session_id": session.id,

        "period": period,

        "class_name": class_name,

        "subject": subject.subject_name,

        "students": data

    })

from .models import Attendance

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_attendance(request):

    if request.user.role != "STAFF":
        return Response(
            {"message":"Permission Denied"},
            status=403
        )

    session_id = request.data.get("session_id")

    attendance = request.data.get("attendance")

    if not session_id or not attendance:

        return Response(
            {"message":"Invalid Data"},
            status=400
        )

    session = TimeTable.objects.get(id=session_id)

    for record in attendance:

        student = Student.objects.get(id=record["student_id"])

        Attendance.objects.create(

            session=session,

            student=student,

            status=record["status"]

        )

    return Response({

        "message":"Attendance Saved Successfully"

    })

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Student, Attendance

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_attendance(request):

    if request.user.role != "STUDENT":
        return Response({
            "message": "Permission Denied"
        }, status=403)

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({
            "message": "Student Not Found"
        }, status=404)

    attendance_records = Attendance.objects.filter(student=student)

    total_classes = attendance_records.count()
    present = attendance_records.filter(status="Present").count()
    absent = attendance_records.filter(status="Absent").count()

    percentage = 0

    if total_classes > 0:
        percentage = round((present / total_classes) * 100, 2)

    attendance_data = []

    for record in attendance_records:

        attendance_data.append({

            # "date": record.session.created_at.date(),

            "period": record.session.period,

            "subject": record.session.subject.subject_name,

            "status": record.status

        })

    return Response({

        "student_name": student.student_name,

        "register_no": student.register_no,

        "total_classes": total_classes,

        "present": present,

        "absent": absent,

        "attendance_percentage": percentage,

        "attendance": attendance_data

    })