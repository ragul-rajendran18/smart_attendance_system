from datetime import time ,datetime
import uuid

from django.utils import timezone
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.http import HttpResponse

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import User, Student, Staff, Subject, AttendanceSession, Attendance, Batch, Holiday
from .permissions import IsAdminRole
from .serializer import LoginSerializer, StudentSerializer, StaffSerializer, BatchSerializer, HolidaySerializer
from .utils import generate_username, generate_password
from .services.student_import_service import import_students_from_file, generate_credentials_excel
from .services.staff_import_service import import_staff_from_file
from .services.staff_result_service import generate_staff_import_result_excel


# Period Schedule
PERIOD_SCHEDULE = (
    (1, time(9, 0), time(9, 50)), (2, time(9, 50), time(10, 40)),
    (3, time(10, 55), time(11, 45)), (4, time(11, 45), time(12, 35)),
    (5, time(13, 20), time(14, 10)), (6, time(14, 10), time(15, 0)),
    (7, time(15, 10), time(15, 55)), (8, time(15, 55), time(16, 40)),
)


def get_active_period(current_time=None):
    current_time = current_time or timezone.localtime().time()
    return next((item for item in PERIOD_SCHEDULE if item[1] <= current_time < item[2]), None)


def _staff_required(request):
    return request.user.role == "STAFF"


# ════════════════════════════════════════════════════════════════
# Auth
# ════════════════════════════════════════════════════════════════

@api_view(["POST"])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(
        username=serializer.validated_data["username"],
        password=serializer.validated_data["password"],
    )
    if user is None:
        return Response({"message": "Invalid Username or Password"}, status=status.HTTP_401_UNAUTHORIZED)
    refresh = RefreshToken.for_user(user)
    return Response({
        "message": "Login Successful",
        "role": user.role,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """Return current user info — used for session rehydration on page refresh."""
    user = request.user
    data = {
        "id": user.id,
        "username": user.username,
        "role": user.role,
    }
    if user.role == "STUDENT":
        try:
            s = user.student
            data.update({
                "name": s.student_name,
                "register_no": s.register_no,
                "class_name": s.class_name,
            })
        except Exception:
            pass
    elif user.role == "STAFF":
        try:
            st = user.staff
            data.update({
                "name": st.staff_name,
                "staff_id": st.staff_id,
            })
        except Exception:
            pass
    elif user.role == "ADMIN":
        data["name"] = user.get_full_name() or user.username
    return Response({"success": True, "data": data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """Blacklist the refresh token so it cannot be reused after logout."""
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({"message": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError:
        pass  # already expired or invalid — still return success
    return Response({"message": "Logged out successfully"})


@api_view(["GET"])
@permission_classes([IsAdminRole])
def admin_dashboard(request):
    """Summary stats for the admin landing dashboard."""
    today = timezone.localdate()
    upcoming_holidays = Holiday.objects.filter(date__gte=today).count()
    return Response({
        "success": True,
        "data": {
            "total_students": Student.objects.count(),
            "total_staff": Staff.objects.count(),
            "total_subjects": Subject.objects.count(),
            "total_batches": Batch.objects.filter(is_active=True).count(),
            "todays_sessions": AttendanceSession.objects.filter(date=today).count(),
            "todays_completed": AttendanceSession.objects.filter(
                date=today, status="COMPLETED"
            ).count(),
            "upcoming_holidays": upcoming_holidays,
        },
    })


# ════════════════════════════════════════════════════════════════
# Student Management
# ════════════════════════════════════════════════════════════════

@api_view(["POST"])
@permission_classes([IsAdminRole])
def create_student(request):
    serializer = StudentSerializer(data=request.data)
    if serializer.is_valid():
        username = generate_username("STU")
        password = generate_password()
        user = User.objects.create(username=username, password=make_password(password), role="STUDENT")
        Student.objects.create(user=user, **serializer.validated_data)
        return Response({"message": "Student Created Successfully", "username": username, "password": password}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_profile(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({"message": "Student Profile Not Found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"student_name": student.student_name, "register_no": student.register_no, "class_name": student.class_name, "username": request.user.username, "role": request.user.role})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_attendance(request):
    if request.user.role != "STUDENT":
        return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({"message": "Student Not Found"}, status=status.HTTP_404_NOT_FOUND)
    records = Attendance.objects.filter(student=student).select_related("session__subject")
    present = records.filter(status="Present").count()
    absent = records.filter(status="Absent").count()
    return Response({"student_name": student.student_name, "register_no": student.register_no, "total_classes": records.count(), "present": present, "absent": absent, "attendance_percentage": round((present / (present + absent)) * 100, 2) if present + absent else 0, "attendance": [{"period": record.session.period, "subject": record.session.subject.subject_name, "status": record.status} for record in records]})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def today_holiday(request):
    today = timezone.localdate()
    holiday = Holiday.objects.filter(date=today).first()
    if holiday:
        return Response({
            "is_holiday": True,
            "date": holiday.date.strftime("%d/%m/%Y"),
            "reason": holiday.reason,
        })
    return Response({"is_holiday": False})


@api_view(["GET"])
@permission_classes([IsAdminRole])
def student_list(request):
    class_name = request.query_params.get("class_name")
    batch_id = request.query_params.get("batch")
    if not class_name or not batch_id:
        return Response({"message": "class_name and batch are required"}, status=status.HTTP_400_BAD_REQUEST)
    students = Student.objects.filter(class_name=class_name, batch_id=batch_id).select_related("batch").order_by("student_name")
    return Response({"message": "Student list retrieved successfully", "class_name": class_name, "batch_id": batch_id, "total_students": students.count(), "students": [{"id": s.id, "student_name": s.student_name, "register_no": s.register_no, "class_name": s.class_name, "batch_id": s.batch_id, "batch": str(s.batch) if s.batch else None} for s in students]})


@api_view(["PUT"])
@permission_classes([IsAdminRole])
def update_student(request):
    student_id = request.data.get("id")
    if not student_id:
        return Response({"message": "Student id is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({"message": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = StudentSerializer(student, data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    student = serializer.save()
    return Response({"message": "Student updated successfully", "student": {"id": student.id, "student_name": student.student_name, "register_no": student.register_no, "class_name": student.class_name, "batch_id": student.batch_id, "batch": str(student.batch) if student.batch else None}})


@api_view(["DELETE"])
@permission_classes([IsAdminRole])
def delete_student(request):
    student_id = request.data.get("id") or request.query_params.get("id")
    if not student_id:
        return Response({"message": "Student id is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        student = Student.objects.select_related("user").get(id=student_id)
    except Student.DoesNotExist:
        return Response({"message": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
    student.user.delete()
    return Response({"message": "Student deleted successfully"})


@api_view(["POST"])
@permission_classes([IsAdminRole])
@parser_classes([MultiPartParser, FormParser])
def bulk_upload_students(request):
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return Response({"message": "File is required.", "field": "file"}, status=status.HTTP_400_BAD_REQUEST)
    if not uploaded_file.name.lower().endswith((".xlsx", ".csv", ".pdf")):
        return Response({"message": "Unsupported file format. Supported formats: XLSX, CSV, PDF."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        result = import_students_from_file(uploaded_file, admin_user=request.user)
    except ValueError as exc:
        return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        return Response({"message": "Student import failed.", "error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    created = result.get("created_students", [])
    ignored = result.get("ignored_students", [])
    failed = result.get("failed_students", [])
    token = uuid.uuid4().hex
    cache.set(f"student_import:{token}", {"created_students": created, "ignored_students": ignored, "failed_students": failed}, timeout=3600)
    return Response({"message": "Student import completed", "source_file": uploaded_file.name, "created_count": len(created), "ignored_count": len(ignored), "failed_count": len(failed), "created_students": created, "ignored_students": ignored, "failed_students": failed, "download_token": token, "download_url": f"/api/students/bulk-upload/download/{token}/"})


@api_view(["GET"])
@permission_classes([IsAdminRole])
def download_student_import_result(request, token):
    result = cache.get(f"student_import:{token}")
    if not result:
        return Response({"message": "Import result not found or download link has expired."}, status=status.HTTP_404_NOT_FOUND)
    try:
        excel_file = generate_credentials_excel(created_students=result.get("created_students", []), ignored_students=result.get("ignored_students", []), failed_students=result.get("failed_students", []))
    except Exception as exc:
        return Response({"message": "Failed to generate result Excel.", "error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    response = HttpResponse(excel_file.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="student_import_result.xlsx"'
    return response


# ════════════════════════════════════════════════════════════════
# Staff Management
# ════════════════════════════════════════════════════════════════

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
            role="STAFF",
        )
        Staff.objects.create(
            user=user,
            staff_name=serializer.validated_data["staff_name"],
            staff_id=serializer.validated_data["staff_id"],
        )
        return Response({
            "message": "Staff Created Successfully",
            "username": username,
            "password": password,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def staff_profile(request):
    if not _staff_required(request):
        return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        return Response({"message": "Staff Profile Not Found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"staff_name": staff.staff_name, "staff_id": staff.staff_id, "username": request.user.username, "role": request.user.role})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def staff_dashboard(request):
    if not _staff_required(request):
        return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
    staff = Staff.objects.get(user=request.user)
    active_period = get_active_period()
    sessions = AttendanceSession.objects.filter(staff=staff).select_related("subject").order_by("-date", "-period", "-id")[:20]
    session_data = [
        {
            "id": session.id,
            "date": session.date.isoformat(),
            "period": session.period,
            "class_name": session.class_name,
            "subject": session.subject.subject_name,
            "status": session.status,
        }
        for session in sessions
    ]
    response_data = {"sessions": session_data}
    if active_period is None:
        response_data["message"] = "No Active Session"
        return Response(response_data)
    period, start, end = active_period
    response_data.update({
        "status": "LIVE",
        "period": period,
        "start_time": start.strftime("%H:%M"),
        "end_time": end.strftime("%H:%M"),
    })
    return Response(response_data)


@api_view(["GET"])
@permission_classes([IsAdminRole])
def staff_list(request):
    staff_members = Staff.objects.select_related("user").all()
    return Response({"staff": [
        {
            "id": staff.id,
            "staff_name": staff.staff_name,
            "staff_id": staff.staff_id,
            "username": staff.user.username,
        }
        for staff in staff_members
    ]})


@api_view(["PUT"])
@permission_classes([IsAdminRole])
def update_staff(request):
    staff_id = request.data.get("id")
    if not staff_id:
        return Response({"message": "Staff id is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        staff = Staff.objects.select_related("user").get(id=staff_id)
    except Staff.DoesNotExist:
        return Response({"message": "Staff not found"}, status=status.HTTP_404_NOT_FOUND)
    
    staff_name = request.data.get("staff_name")
    staff_code = request.data.get("staff_id")
    password = request.data.get("password")
    
    if staff_name:
        staff.staff_name = staff_name
    if staff_code:
        if Staff.objects.filter(staff_id=staff_code).exclude(id=staff_id).exists():
            return Response({"message": "Staff ID already exists"}, status=status.HTTP_400_BAD_REQUEST)
        staff.staff_id = staff_code
    if password:
        staff.user.password = make_password(password)
        staff.user.save()
    
    staff.save()
    return Response({
        "message": "Staff updated successfully",
        "staff": {
            "id": staff.id,
            "staff_name": staff.staff_name,
            "staff_id": staff.staff_id,
            "username": staff.user.username,
        }
    })


@api_view(["DELETE"])
@permission_classes([IsAdminRole])
def delete_staff(request):
    staff_id = request.data.get("id") or request.query_params.get("id")
    if not staff_id:
        return Response({"message": "Staff id is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        staff = Staff.objects.select_related("user").get(id=staff_id)
    except Staff.DoesNotExist:
        return Response({"message": "Staff not found"}, status=status.HTTP_404_NOT_FOUND)
    staff.user.delete()
    return Response({"message": "Staff deleted successfully"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def session_list(request):
    if not _staff_required(request):
        return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
    sessions = AttendanceSession.objects.filter(staff__user=request.user).select_related("subject").prefetch_related("attendance_set").order_by("-date", "-period", "-id")
    return Response({"sessions": [{
        "id": session.id, "period": session.period, "class_name": session.class_name,
        "subject": session.subject.subject_name, "date": session.date.isoformat(),
        "status": session.status,
        "present_count": sum(record.status == "Present" for record in session.attendance_set.all()),
        "absent_count": sum(record.status == "Absent" for record in session.attendance_set.all()),
    } for session in sessions]})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def session_attendance(request):
    if not _staff_required(request):
        return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
    session_id = request.query_params.get("session_id")
    if not session_id:
        return Response({"message": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        session = AttendanceSession.objects.select_related("subject").get(id=session_id, staff__user=request.user)
    except (AttendanceSession.DoesNotExist, ValueError):
        return Response({"message": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
    records = Attendance.objects.filter(session=session).select_related("student").order_by("student__register_no")
    return Response({"session": {"id": session.id, "period": session.period, "class_name": session.class_name, "subject": session.subject.subject_name, "date": session.date.isoformat(), "status": session.status}, "students": [
        {"id": record.student_id, "student_name": record.student.student_name, "register_no": record.student.register_no, "status": record.status}
        for record in records
    ]})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subject_list(request):
    class_name = request.query_params.get("class_name", "").strip()
    qs = Subject.objects.all().order_by("class_name", "subject_name")
    if class_name:
        qs = qs.filter(class_name=class_name)
    return Response({
        "subjects": [
            {
                "id": subject.id,
                "subject_code": subject.subject_code,
                "subject_name": subject.subject_name,
                "class_name": subject.class_name,
            }
            for subject in qs
        ]
    })


@api_view(["PUT"])
@permission_classes([IsAdminRole])
def update_subject(request):
    subject_id = request.data.get("id")
    if not subject_id:
        return Response({"message": "Subject id is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return Response({"message": "Subject not found"}, status=status.HTTP_404_NOT_FOUND)

    subject_code = request.data.get("subject_code")
    subject_name = request.data.get("subject_name")
    class_name = request.data.get("class_name")

    if subject_code:
        if Subject.objects.filter(subject_code=subject_code).exclude(id=subject_id).exists():
            return Response({"message": "Subject code already exists"}, status=status.HTTP_400_BAD_REQUEST)
        subject.subject_code = subject_code
    if subject_name:
        subject.subject_name = subject_name
    if class_name:
        subject.class_name = class_name

    subject.save()
    return Response({
        "message": "Subject updated successfully",
        "subject": {
            "id": subject.id,
            "subject_code": subject.subject_code,
            "subject_name": subject.subject_name,
            "class_name": subject.class_name,
        },
    })


@api_view(["DELETE"])
@permission_classes([IsAdminRole])
def delete_subject(request):
    subject_id = request.data.get("id") or request.query_params.get("id")
    if not subject_id:
        return Response({"message": "Subject id is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return Response({"message": "Subject not found"}, status=status.HTTP_404_NOT_FOUND)
    subject.delete()
    return Response({"message": "Subject deleted successfully"})


@api_view(["POST"])
@permission_classes([IsAdminRole])
def create_subject(request):
    subject_code = request.data.get("subject_code")
    subject_name = request.data.get("subject_name")
    class_name = request.data.get("class_name")
    if not subject_code or not subject_name or not class_name:
        field = "Subject code" if not subject_code else "Subject name" if not subject_name else "Class name"
        return Response({"message": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST)
    if Subject.objects.filter(subject_code=subject_code).exists():
        return Response({"message": "Subject code already exists"}, status=status.HTTP_400_BAD_REQUEST)
    subject = Subject.objects.create(
        subject_code=subject_code,
        subject_name=subject_name,
        class_name=class_name,
    )
    return Response({
        "message": "Subject Created Successfully",
        "subject": {
            "id": subject.id,
            "subject_code": subject.subject_code,
            "subject_name": subject.subject_name,
            "class_name": subject.class_name,
        },
    }, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAdminRole])
def create_batch(request):
    serializer = BatchSerializer(data=request.data)
    if serializer.is_valid():
        batch = serializer.save()
        return Response({
            "message": "Batch Created Successfully",
            "batch": {"id": batch.id, "name": batch.name, "is_active": batch.is_active},
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAdminRole])
def list_batches(request):
    return Response([
        {"id": batch.id, "name": batch.name}
        for batch in Batch.objects.filter(is_active=True).order_by("name")
    ])


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def staff_classes(request):
    if not _staff_required(request):
        return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
    return Response({"classes": list(Subject.objects.values_list("class_name", flat=True).distinct().order_by("class_name"))})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def class_subjects(request):
    if not _staff_required(request):
        return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
    class_name = request.query_params.get("class_name", "").strip()
    if not class_name:
        return Response({"message": "class_name is required"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"class_name": class_name, "subjects": [
        {"id": subject.id, "subject_code": subject.subject_code, "subject_name": subject.subject_name}
        for subject in Subject.objects.filter(class_name=class_name).order_by("subject_name")
    ]})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_session(request):
    if not _staff_required(request):
        return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
    today = timezone.localdate()
    holiday = Holiday.objects.filter(date=today).first()
    if holiday:
        return Response(
            {
                "message": "Today is a holiday. Attendance session cannot be started.",
                "date": today.strftime("%d/%m/%Y"),
                "reason": holiday.reason
            },
            status=status.HTTP_403_FORBIDDEN
        )
    try:
        staff = Staff.objects.get(user=request.user)
        subject = Subject.objects.get(id=request.data.get("subject_id"))
    except (Staff.DoesNotExist, Subject.DoesNotExist, ValueError):
        return Response({"message": "Subject Not Found"}, status=status.HTTP_404_NOT_FOUND)
    class_name = request.data.get("class_name")
    if not class_name or not request.data.get("subject_id"):
        return Response({"message": "class_name and subject_id are required"}, status=status.HTTP_400_BAD_REQUEST)
    if subject.class_name != class_name:
        return Response({"message": "Subject does not belong to the selected class"}, status=status.HTTP_400_BAD_REQUEST)
    active_period = get_active_period()
    if active_period is None:
        return Response({"message": "No Active Session"}, status=status.HTTP_400_BAD_REQUEST)
    period, _, _ = active_period
    session = AttendanceSession.objects.filter(staff=staff, date=timezone.localdate(), period=period).select_related("subject").first()
    if session and (session.class_name != class_name or session.subject_id != subject.id):
        return Response({"message": "Another session is already started for this period."}, status=status.HTTP_409_CONFLICT)
    message = "Existing session loaded." if session else "Session Started Successfully"
    if not session:
        session = AttendanceSession.objects.create(staff=staff, class_name=class_name, subject=subject, date=timezone.localdate(), period=period, status="ACTIVE")
    students = Student.objects.filter(class_name=session.class_name).order_by("student_name")
    return Response({"message": message, "session_id": session.id, "period": session.period, "class_name": session.class_name, "subject": session.subject.subject_name, "students": [{"id": s.id, "student_name": s.student_name, "register_no": s.register_no} for s in students]})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_attendance(request):
    if not _staff_required(request):
        return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
    session_id = request.data.get("session_id")
    attendance = request.data.get("attendance")
    if not session_id or not attendance:
        return Response({"message": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        session = AttendanceSession.objects.get(id=session_id, staff__user=request.user)
    except (AttendanceSession.DoesNotExist, ValueError):
        return Response({"message": "Attendance session not found"}, status=status.HTTP_404_NOT_FOUND)
    for record in attendance:
        Attendance.objects.update_or_create(session=session, student_id=record["student_id"], defaults={"status": record["status"]})
    session.status = "COMPLETED"
    session.save(update_fields=["status"])
    return Response({"message": "Attendance Saved Successfully"})

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def edit_attendance(request):

    if not _staff_required(request):
        return Response(
            {"message": "Permission Denied"},
            status=status.HTTP_403_FORBIDDEN
        )

    session_id = request.data.get("session_id")
    attendance_data = request.data.get("attendance")

    if not session_id or not attendance_data:
        return Response(
            {
                "message": "session_id and attendance are required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        session = AttendanceSession.objects.get(
            id=session_id,
            staff__user=request.user
        )

    except (AttendanceSession.DoesNotExist, ValueError):
        return Response(
            {
                "message": "Attendance session not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # Check current active period
    active_period = get_active_period()

    if active_period is None:
        return Response(
            {
                "message": "Attendance editing is not allowed outside the session time"
            },
            status=status.HTTP_403_FORBIDDEN
        )

    current_period, _, _ = active_period
    # Current period must match the attendance session period
    if session.period != current_period:
        return Response(
            {
                "message": "Attendance can only be edited during its active session period"
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # Make sure it is today's session
    if session.date != timezone.localdate():
        return Response(
            {
                "message": "Attendance can only be edited on the session date"
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # Update attendance
    for record in attendance_data:
        student_id = record.get("student_id")
        attendance_status = record.get("status")

        if not student_id or attendance_status not in ["Present", "Absent"]:
            return Response(
                {
                    "message": "Invalid attendance data"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        # Verify student belongs to this session class
        if not Student.objects.filter(
            id=student_id,
            class_name=session.class_name
        ).exists():

            return Response(
                {
                    "message": f"Student {student_id} does not belong to this class"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        Attendance.objects.update_or_create(
            session=session,
            student_id=student_id,
            defaults={
                "status": attendance_status
            }
        )
    return Response(
        {
            "message": "Attendance Updated Successfully",
            "session_id": session.id,
            "period": session.period
        },
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([IsAdminRole])
@parser_classes([MultiPartParser, FormParser])
def bulk_upload_staff(request):
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return Response({"message": "File is required.", "field": "file"}, status=status.HTTP_400_BAD_REQUEST)
    if not uploaded_file.name.lower().endswith((".xlsx", ".csv", ".pdf")):
        return Response({"message": "Unsupported file format. Supported formats: XLSX, CSV, PDF."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        result = import_staff_from_file(uploaded_file, admin_user=request.user)
    except ValueError as exc:
        return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        return Response({"message": "Staff import failed.", "error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    created = result.get("created_staff", [])
    ignored = result.get("ignored_staff", [])
    failed = result.get("failed_staff", [])
    token = uuid.uuid4().hex
    cache.set(f"staff_import:{token}", {"created_staff": created, "ignored_staff": ignored, "failed_staff": failed}, timeout=3600)
    return Response({
        "message": "Staff import completed",
        "source_file": uploaded_file.name,
        "created_count": len(created),
        "ignored_count": len(ignored),
        "failed_count": len(failed),
        "created_staff": created,
        "ignored_staff": ignored,
        "failed_staff": failed,
        "download_token": token,
        "download_url": f"/api/staff/bulk-upload/download/{token}/",
    })


@api_view(["GET"])
@permission_classes([IsAdminRole])
def download_staff_import_result(request, token):
    result = cache.get(f"staff_import:{token}")
    if not result:
        return Response({"message": "Import result not found or expired."}, status=status.HTTP_404_NOT_FOUND)
    try:
        excel_file = generate_staff_import_result_excel(
            created_staff=result.get("created_staff", []),
            ignored_staff=result.get("ignored_staff", []),
            failed_staff=result.get("failed_staff", []),
        )
    except Exception as exc:
        return Response({"message": "Failed to generate Excel result.", "error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    response = HttpResponse(excel_file.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="staff_import_result.xlsx"'
    return response

@api_view(["POST"])
@permission_classes([IsAdminRole])
def create_holiday(request):

    date = request.data.get("date")
    reason = request.data.get("reason")

    if not date or not reason:
        return Response(
            {
                "message": "date and reason are required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        holiday_date = datetime.strptime(
            date,
            "%d/%m/%Y"
        ).date()

    except ValueError:
        return Response(
            {
                "message": "Invalid date format. Use DD/MM/YYYY"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if Holiday.objects.filter(date=holiday_date).exists():

        return Response(
            {
                "message": "Holiday already exists for this date"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    holiday = Holiday.objects.create(
        date=holiday_date,
        reason=reason
    )

    return Response(
        {
            "message": "Holiday created successfully",
            "id": holiday.id,
            "date": holiday.date.strftime("%d/%m/%Y"),
            "reason": holiday.reason
        },
        status=status.HTTP_201_CREATED
    )


@api_view(["GET"])
@permission_classes([IsAdminRole])
def list_holidays(request):
    holidays = Holiday.objects.all().order_by("-date")
    return Response({
        "holidays": [
            {
                "id": h.id,
                "date": h.date.strftime("%d/%m/%Y"),
                "reason": h.reason,
            }
            for h in holidays
        ]
    })


@api_view(["DELETE"])
@permission_classes([IsAdminRole])
def delete_holiday(request):
    holiday_id = request.data.get("id") or request.query_params.get("id")
    if not holiday_id:
        return Response(
            {"message": "Holiday id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        holiday = Holiday.objects.get(id=holiday_id)
    except Holiday.DoesNotExist:
        return Response(
            {"message": "Holiday not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    holiday.delete()
    return Response({"message": "Holiday deleted successfully"})