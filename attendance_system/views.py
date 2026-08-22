from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.conf import settings
from io import BytesIO
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminRole
from rest_framework.response import Response
from rest_framework import status
from .models import User, Student, Staff, Subject, AttendanceSession, Attendance, Batch
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import time, timedelta
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
@permission_classes([IsAdminRole])
def weekly_report(request):
    class_name = request.query_params.get("class_name", "").strip()
    batch_id = request.query_params.get("batch", "").strip()
    start_date = request.query_params.get("start_date", "").strip()
    end_date = request.query_params.get("end_date", "").strip()

    if not class_name or not batch_id or not start_date or not end_date:
        return Response({
            "message": "class_name, batch, start_date and end_date are required"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        batch = Batch.objects.get(id=batch_id, is_active=True)
    except (Batch.DoesNotExist, ValueError):
        return Response({"message": "Active batch not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return Response({"message": "Dates must use YYYY-MM-DD format"}, status=status.HTTP_400_BAD_REQUEST)
    if start > end:
        return Response({"message": "start_date must be before end_date"}, status=status.HTTP_400_BAD_REQUEST)

    students = list(
        Student.objects.filter(class_name=class_name, batch=batch)
        .order_by("register_no")
    )
    sessions = list(
        AttendanceSession.objects.filter(
            class_name=class_name,
            date__range=(start, end),
            status="COMPLETED",
        )
        .select_related("staff", "subject")
        .order_by("date", "period", "id")
    )

    sessions_by_slot = {}
    for session in sessions:
        sessions_by_slot.setdefault((session.date, session.period), session)

    attendance_by_slot_student = {
        (record.session.date.isoformat(), record.session.period, record.student_id): record.status
        for record in Attendance.objects.filter(
            session__in=sessions,
            student__in=students,
        ).select_related("session")
    }

    slots = []
    current_date = start
    while current_date <= end:
        for period in range(1, 9):
            session = sessions_by_slot.get((current_date, period))
            slots.append({
                "date": current_date.isoformat(),
                "day": current_date.strftime("%A"),
                "period": period,
                "staff": session.staff.staff_name if session else "N/C",
                "subject_code": session.subject.subject_code if session else "N/C",
                "subject": session.subject.subject_name if session else "N/C",
                "session_id": session.id if session else None,
            })
        current_date += timedelta(days=1)

    student_rows = []
    counted_slots = len(sessions_by_slot)
    for student in students:
        attendance = {}
        present = 0
        absent = 0
        for slot in slots:
            key = (slot["date"], slot["period"], student.id)
            value = attendance_by_slot_student.get(key, "M" if slot["session_id"] else "N/C")
            attendance[f"{slot['date']}_P{slot['period']}"] = value
            if value == "Present":
                present += 1
            elif value == "Absent":
                absent += 1

        student_rows.append({
            "register_no": student.register_no,
            "student_name": student.student_name,
            "attendance": attendance,
            "total_classes": counted_slots,
            "present": present,
            "absent": absent,
            "missing": counted_slots - present - absent,
            "attendance_percentage": round((present / (present + absent)) * 100, 2) if present + absent else 0,
        })

    return Response({
        "class_name": class_name,
        "batch": {"id": batch.id, "name": batch.name},
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "slots": slots,
        "students": student_rows,
    })


@api_view(["GET"])
@permission_classes([IsAdminRole])
def weekly_report_excel(request):
    report = weekly_report(request)
    if report.status_code != status.HTTP_200_OK:
        return report

    report_data = report.data
    slots = report_data["slots"]
    dates = []
    for slot in slots:
        if slot["date"] not in dates:
            dates.append(slot["date"])

    if len(dates) > 6:
        return Response({
            "message": "The Excel template supports a maximum of 6 dates"
        }, status=status.HTTP_400_BAD_REQUEST)

    from openpyxl import load_workbook

    template_path = settings.BASE_DIR / "III IT B WEEKLY ATT.xlsx"
    workbook = load_workbook(template_path)
    worksheet = workbook["Master"]

    for merged_range in list(worksheet.merged_cells.ranges):
        if merged_range.min_row in (8, 9) and merged_range.max_row <= 9:
            if merged_range.min_col >= 5 and merged_range.max_col <= 50:
                worksheet.unmerge_cells(str(merged_range))

    worksheet["A3"] = "Weekly Attendance Report"
    worksheet["A4"] = (
        f"Attendance From: {report_data['start_date']} "
        f"to {report_data['end_date']}"
    )
    worksheet["U4"] = f"BATCH: {report_data['batch']['name']}"
    worksheet["AL4"] = f"CLASS: {report_data['class_name']}"

    for column in range(5, 51):
        worksheet.cell(8, column).value = "N/C"
        worksheet.cell(9, column).value = "N/C"

    slot_by_key = {
        (slot["date"], slot["period"]): slot
        for slot in slots
    }
    for date_index, report_date in enumerate(dates):
        first_column = 5 + date_index * 8
        worksheet.cell(5, first_column).value = report_date
        worksheet.cell(6, first_column).value = datetime.strptime(
            report_date, "%Y-%m-%d"
        ).strftime("%A").upper()
        for period in range(1, 9):
            column = first_column + period - 1
            slot = slot_by_key[(report_date, period)]
            worksheet.cell(7, column).value = period
            worksheet.cell(8, column).value = (
                f"{slot['subject_code']} - {slot['subject']}"
                if slot["session_id"] else "N/C"
            )
            worksheet.cell(9, column).value = (
                f"Staff: {slot['staff']}"
                if slot["session_id"] else "N/C"
            )

    if len(report_data["students"]) > worksheet.max_row - 9:
        return Response({
            "message": "The Excel template supports a maximum of 71 students"
        }, status=status.HTTP_400_BAD_REQUEST)

    for row in range(10, worksheet.max_row + 1):
        for column in range(1, 56):
            if column != 3:
                worksheet.cell(row, column).value = None
        worksheet.cell(row, 3).value = None

    for row_number, student in enumerate(report_data["students"], start=10):
        worksheet.cell(row_number, 1).value = student["register_no"]
        worksheet.cell(row_number, 2).value = student["student_name"]
        worksheet.cell(row_number, 3).value = None
        worksheet.cell(row_number, 4).value = 0

        present = 0
        for date_index, report_date in enumerate(dates):
            first_column = 5 + date_index * 8
            for period in range(1, 9):
                key = f"{report_date}_P{period}"
                value = student["attendance"].get(key, "N/C")
                if value == "Present":
                    cell_value = 1
                    present += 1
                elif value == "Absent":
                    cell_value = "a"
                else:
                    cell_value = value
                worksheet.cell(row_number, first_column + period - 1).value = cell_value

        worksheet.cell(row_number, 51).value = present
        worksheet.cell(row_number, 52).value = present
        worksheet.cell(row_number, 53).value = (
            round((present / (present + student["absent"])) * 100, 2)
            if present + student["absent"] else 0
        )

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f"attachment; filename=weekly_report_{report_data['batch']['name']}.xlsx"
    )
    return response


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