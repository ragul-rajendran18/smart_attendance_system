from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminRole
from rest_framework.response import Response
from rest_framework import status
from .models import User, Student, Staff, Subject, AttendanceSession, Attendance, Batch
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import time
from .models import User, Student, Staff
from .serializer import (
    StudentSerializer,
    StaffSerializer,
    LoginSerializer,
    TimeTableSerializer,
    BatchSerializer
)
from .utils import generate_username, generate_password
from datetime import datetime
from .models import TimeTable

import uuid
from django.core.cache import cache

from django.http import HttpResponse

from rest_framework.decorators import (
    api_view,
    permission_classes,
    parser_classes,
)
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
)
from rest_framework.response import Response
from rest_framework import status

from .permissions import IsAdminRole

from .services.student_import_service import (
    import_students_from_file,
    generate_credentials_excel,
)
from .permissions import IsAdminRole

from .services.staff_import_service import (
    import_staff_from_file,
)

from .services.staff_result_service import (
    generate_staff_import_result_excel,
)
import json
import zipfile
from io import BytesIO


PERIOD_SCHEDULE = (
    (1, time(9, 0), time(9, 50)),
    (2, time(9, 50), time(10, 40)),
    (3, time(10, 55), time(11, 45)),
    (4, time(11, 45), time(12, 35)),
    (5, time(13, 20), time(14, 10)),
    (6, time(14, 10), time(15, 0)),
    (7, time(15, 10), time(15, 55)),
    (8, time(15, 55), time(16, 40)),
)


def get_active_period(current_time=None):
    current_time = current_time or timezone.localtime().time()
    for period, start, end in PERIOD_SCHEDULE:
        if start <= current_time < end:
            return period, start, end
    return None


# ============================
# Create Student
# ============================

@api_view(["POST"])
@permission_classes([IsAdminRole])
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
            class_name=serializer.validated_data["class_name"],
            batch=serializer.validated_data["batch"],
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
@permission_classes([IsAdminRole])
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


@api_view(["POST"])
@permission_classes([IsAdminRole])
def create_subject(request):

    subject_code = request.data.get("subject_code")
    subject_name = request.data.get("subject_name")
    class_name = request.data.get("class_name")

    if not subject_code:
        return Response(
            {"message": "Subject code is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not subject_name:
        return Response(
            {"message": "Subject name is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not class_name:
        return Response(
            {"message": "Class name is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if Subject.objects.filter(
        subject_code=subject_code
    ).exists():

        return Response(
            {"message": "Subject code already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )

    subject = Subject.objects.create(
        subject_code=subject_code,
        subject_name=subject_name,
        class_name=class_name
    )

    return Response({

        "message": "Subject Created Successfully",

        "subject": {
            "id": subject.id,
            "subject_code": subject.subject_code,
            "subject_name": subject.subject_name,
            "class_name": subject.class_name
        }

    }, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAdminRole])
def create_batch(request):
    serializer = BatchSerializer(data=request.data)

    if serializer.is_valid():
        batch = serializer.save()
        return Response({
            "message": "Batch Created Successfully",
            "batch": {
                "id": batch.id,
                "name": batch.name,
                "is_active": batch.is_active,
            },
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAdminRole])
def list_batches(request):
    batches = Batch.objects.filter(is_active=True).order_by("name")
    return Response([
        {"id": batch.id, "name": batch.name}
        for batch in batches
    ])


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def staff_classes(request):
    if request.user.role != "STAFF":
        return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)

    classes = Subject.objects.values_list("class_name", flat=True).distinct().order_by("class_name")
    return Response({"classes": list(classes)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def class_subjects(request):
    if request.user.role != "STAFF":
        return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)

    class_name = request.query_params.get("class_name", "").strip()
    if not class_name:
        return Response({"message": "class_name is required"}, status=status.HTTP_400_BAD_REQUEST)

    subjects = Subject.objects.filter(class_name=class_name).order_by("subject_name")
    return Response({
        "class_name": class_name,
        "subjects": [
            {
                "id": subject.id,
                "subject_code": subject.subject_code,
                "subject_name": subject.subject_name,
            }
            for subject in subjects
        ],
    })

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
            {"message": "Permission Denied"},
            status=status.HTTP_403_FORBIDDEN
        )

    current_time = datetime.now().time()
    print(current_time)

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
     active_period = get_active_period()
    if active_period is None:
        return Response({
             "message": "No Active Session"
        })

    period, start, end = active_period

    return Response({
        "status": "LIVE",
        "period": period,
        "start_time": start.strftime("%H:%M"),
        "end_time": end.strftime("%H:%M"),
    })

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

    if subject.class_name != class_name:
        return Response(
            {"message": "Subject does not belong to the selected class"},
            status=status.HTTP_400_BAD_REQUEST
        )

    current_day = timezone.localtime().strftime("%A")
    active_period = get_active_period()
    if active_period is None:
        return Response(
            {"message": "No Active Session"},
            status=status.HTTP_400_BAD_REQUEST
        )

    period, start, end = active_period

    existing_session = AttendanceSession.objects.filter(
        staff=staff,
        date=timezone.localdate(),
        period=period
    ).select_related("subject").first()

    if existing_session and (
        existing_session.class_name != class_name
        or existing_session.subject_id != subject.id
    ):
        return Response(
            {"message": "Another session is already started for this period."},
            status=status.HTTP_409_CONFLICT
        )

    if existing_session:
        session = existing_session
        message = "Existing session loaded."
    else:
        session = AttendanceSession.objects.create(
            staff=staff,
            class_name=class_name,
            subject=subject,
            date=timezone.localdate(),
            period=period,
            status="ACTIVE"
        )
        message = "Session Started Successfully"

    students = Student.objects.filter(class_name=session.class_name).order_by("student_name")

    data = []

    for student in students:
        data.append({
            "id": student.id,
            "student_name": student.student_name,
            "register_no": student.register_no
        })

    return Response({

        "message": message,

        "session_id": session.id,

        "period": session.period,

        "class_name": session.class_name,

        "subject": session.subject.subject_name,

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

    try:
        session = AttendanceSession.objects.get(id=session_id, staff__user=request.user)
    except AttendanceSession.DoesNotExist:
        return Response({"message": "Attendance session not found"}, status=404)

    for record in attendance:

        student = Student.objects.get(id=record["student_id"])

        Attendance.objects.update_or_create(
            session=session,
            student=student,
            defaults={"status": record["status"]}
        )

    session.status = "COMPLETED"
    session.save(update_fields=["status"])

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

@api_view(["POST"])
@permission_classes([IsAdminRole])
@parser_classes([MultiPartParser, FormParser])
def bulk_upload_students(request):

    # ========================================================
    # 1. GET FILE
    # ========================================================

    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return Response(
            {
                "message": "File is required.",
                "field": "file",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ========================================================
    # 2. VALIDATE FILE
    # ========================================================

    filename = uploaded_file.name.lower()

    allowed_extensions = (
        ".xlsx",
        ".csv",
        ".pdf",
    )

    if not filename.endswith(allowed_extensions):
        return Response(
            {
                "message": (
                    "Unsupported file format. "
                    "Supported formats: XLSX, CSV, PDF."
                ),
                "filename": uploaded_file.name,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ========================================================
    # 3. IMPORT STUDENTS
    # ========================================================

    try:

        result = import_students_from_file(
            uploaded_file,
            admin_user=request.user,
        )

    except ValueError as exc:

        return Response(
            {
                "message": str(exc),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as exc:

        return Response(
            {
                "message": "Student import failed.",
                "error": str(exc),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # ========================================================
    # 4. GET RESULT
    # ========================================================

    created_students = result.get(
        "created_students",
        []
    )

    ignored_students = result.get(
        "ignored_students",
        []
    )

    failed_students = result.get(
        "failed_students",
        []
    )

    # ========================================================
    # 5. CREATE DOWNLOAD TOKEN
    # ========================================================

    download_token = uuid.uuid4().hex

    # Store only temporarily.
    #
    # 1 hour = 3600 seconds
    #
    cache.set(
        f"student_import:{download_token}",
        {
            "created_students": created_students,
            "ignored_students": ignored_students,
            "failed_students": failed_students,
        },
        timeout=3600,
    )

    # ========================================================
    # 6. RETURN JSON
    # ========================================================

    return Response(
        {
            "message": "Student import completed",

            "source_file": uploaded_file.name,

            "created_count": len(
                created_students
            ),

            "ignored_count": len(
                ignored_students
            ),

            "failed_count": len(
                failed_students
            ),

            "created_students": created_students,

            "ignored_students": ignored_students,

            "failed_students": failed_students,

            "download": {
                "available": True,
                "token": download_token,
                "expires_in": 3600,
                "endpoint": (
                    f"/api/students/"
                    f"bulk-upload/download/"
                    f"{download_token}/"
                ),
            },
        },
        status=status.HTTP_200_OK,
    )

@api_view(["GET"])
@permission_classes([IsAdminRole])
def download_student_import_result(request, token):

    # ========================================================
    # 1. GET STORED IMPORT RESULT
    # ========================================================

    cache_key = f"student_import:{token}"

    import_result = cache.get(cache_key)

    if not import_result:

        return Response(
            {
                "message": (
                    "Import result not found or "
                    "download link has expired."
                ),
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # ========================================================
    # 2. GET DATA
    # ========================================================

    created_students = import_result.get(
        "created_students",
        []
    )

    ignored_students = import_result.get(
        "ignored_students",
        []
    )

    failed_students = import_result.get(
        "failed_students",
        []
    )

    # ========================================================
    # 3. GENERATE EXCEL
    # ========================================================

    try:

        excel_file = generate_credentials_excel(
            created_students=created_students,
            ignored_students=ignored_students,
            failed_students=failed_students,
        )

    except Exception as exc:

        return Response(
            {
                "message": "Failed to generate result Excel.",
                "error": str(exc),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # ========================================================
    # 4. RETURN EXCEL
    # ========================================================

    response = HttpResponse(
        excel_file.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

    response["Content-Disposition"] = (
        'attachment; filename="student_import_result.xlsx"'
    )

    return response
from django.core.cache import cache
from django.http import HttpResponse

from rest_framework.decorators import (
    api_view,
    permission_classes,
    parser_classes,
)
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status




@api_view(["POST"])
@permission_classes([IsAdminRole])
@parser_classes([MultiPartParser, FormParser])
def bulk_upload_staff(request):

    uploaded_file = request.FILES.get(
        "file"
    )

    if not uploaded_file:

        return Response(
            {
                "message": "File is required.",
                "field": "file",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    filename = (
        uploaded_file.name
        .lower()
        .strip()
    )

    allowed_extensions = (
        ".xlsx",
        ".csv",
        ".pdf",
    )

    if not filename.endswith(
        allowed_extensions
    ):

        return Response(
            {
                "message": (
                    "Unsupported file format. "
                    "Supported formats: XLSX, CSV, PDF."
                ),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:

        result = import_staff_from_file(
            uploaded_file,
            admin_user=request.user,
        )

    except ValueError as exc:

        return Response(
            {
                "message": str(exc),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as exc:

        return Response(
            {
                "message": "Staff import failed.",
                "error": str(exc),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    created_staff = result.get(
        "created_staff",
        [],
    )

    ignored_staff = result.get(
        "ignored_staff",
        [],
    )

    failed_staff = result.get(
        "failed_staff",
        [],
    )

    # ========================================================
    # DOWNLOAD TOKEN
    # ========================================================

    token = uuid.uuid4().hex

    cache.set(
        f"staff_import:{token}",
        {
            "created_staff": created_staff,
            "ignored_staff": ignored_staff,
            "failed_staff": failed_staff,
        },
        timeout=3600,
    )

    return Response(
        {
            "message": "Staff import completed",

            "source_file": uploaded_file.name,

            "created_count": len(
                created_staff
            ),

            "ignored_count": len(
                ignored_staff
            ),

            "failed_count": len(
                failed_staff
            ),

            "created_staff": created_staff,

            "ignored_staff": ignored_staff,

            "failed_staff": failed_staff,

            "download_token": token,

            "download_url": (
                "/api/staff/bulk-upload/"
                f"download/{token}/"
            ),
        },
        status=status.HTTP_200_OK,
    )
@api_view(["GET"])
@permission_classes([IsAdminRole])
def download_staff_import_result(
    request,
    token,
):

    result = cache.get(
        f"staff_import:{token}"
    )

    if not result:

        return Response(
            {
                "message": (
                    "Import result not found "
                    "or expired."
                ),
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    try:

        excel_file = (
            generate_staff_import_result_excel(
                created_staff=result.get(
                    "created_staff",
                    [],
                ),

                ignored_staff=result.get(
                    "ignored_staff",
                    [],
                ),

                failed_staff=result.get(
                    "failed_staff",
                    [],
                ),
            )
        )

    except Exception as exc:

        return Response(
            {
                "message": (
                    "Failed to generate "
                    "Excel result."
                ),

                "error": str(exc),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    response = HttpResponse(
        excel_file.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

    response[
        "Content-Disposition"
    ] = (
        'attachment; '
        'filename="staff_import_result.xlsx"'
    )

    return response