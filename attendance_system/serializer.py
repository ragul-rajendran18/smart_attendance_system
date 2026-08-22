from rest_framework import serializers
from .models import (
    Student,
    Staff,
    Subject,
    StaffSubject,
    TimeTable,
    AttendanceSession,
    Attendance,
    Batch
)


class StudentSerializer(serializers.ModelSerializer):
    batch = serializers.PrimaryKeyRelatedField(
        queryset=Batch.objects.filter(is_active=True)
    )

    class Meta:
        model = Student
        fields = [
            "student_name",
            "register_no",
            "class_name",
            "batch",
        ]

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = [
            "staff_name",
            "staff_id",
        ]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class StaffSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffSubject
        fields = "__all__"


class TimeTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeTable
        fields = "__all__"


class AttendanceSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceSession
        fields = "__all__"


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ["name"]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)