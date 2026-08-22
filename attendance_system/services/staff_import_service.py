from django.contrib.auth.hashers import make_password
from django.db import transaction

from ..models import User, Staff
from ..utils import generate_username, generate_password

from .file_parser_service import parse_file

from .normalization_service import (
    normalize_staff_name,
    normalize_staff_id,
)



# ============================================================
# REQUIRED FIELDS
# ============================================================

REQUIRED_FIELDS = {
    "staff_name",
    "staff_id",
}


from django.db import transaction

from ..models import User, Staff
from ..utils import (
    generate_username,
    generate_password,
)

from .file_parser_service import (
    parse_staff_file,
)

from .normalization_service import (
    normalize_staff_name,
    normalize_staff_id,
)


# ============================================================
# VALIDATION
# ============================================================

def validate_staff_data(data):

    errors = []

    if not data.get("staff_name"):
        errors.append(
            "Staff Name is missing"
        )

    if not data.get("staff_id"):
        errors.append(
            "Staff ID is missing"
        )

    return errors


# ============================================================
# IMPORT STAFF
# ============================================================

@transaction.atomic
def import_staff_from_file(
    uploaded_file,
    admin_user=None,
):

    rows = parse_staff_file(
        uploaded_file
    )

    print(
        "================================"
    )

    print(
        "STAFF PARSER ROW COUNT:",
        len(rows),
    )

    print(
        "STAFF PARSER SAMPLE:",
        rows[:3],
    )

    print(
        "================================"
    )

    created_staff = []
    ignored_staff = []
    failed_staff = []

    # ========================================================
    # PROCESS ROWS
    # ========================================================

    for row in rows:

        staff_name = normalize_staff_name(
            row.get("staff_name")
        )

        staff_id = normalize_staff_id(
            row.get("staff_id")
        )

        data = {
            "staff_name": staff_name,
            "staff_id": staff_id,
        }

        # ----------------------------------------------------
        # EMPTY
        # ----------------------------------------------------

        if not any(data.values()):
            continue

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        errors = validate_staff_data(
            data
        )

        if errors:

            failed_staff.append({
                "sheet": row.get(
                    "_sheet",
                    "",
                ),

                "row": row.get(
                    "_row",
                    None,
                ),

                "staff_id": staff_id,

                "reason": "; ".join(
                    errors
                ),
            })

            continue

        # ----------------------------------------------------
        # DUPLICATE
        # ----------------------------------------------------

        existing_staff = (
            Staff.objects
            .filter(
                staff_id=staff_id
            )
            .first()
        )

        if existing_staff:

            ignored_staff.append({
                "staff_id": (
                    existing_staff.staff_id
                ),

                "staff_name": (
                    existing_staff.staff_name
                ),

                "reason": (
                    "Staff ID already exists"
                ),
            })

            continue

        # ----------------------------------------------------
        # CREDENTIALS
        # ----------------------------------------------------

        username = generate_username(
            "STF"
        )

        raw_password = generate_password()

        # ----------------------------------------------------
        # USER
        # ----------------------------------------------------

        user = User(
            username=username,
            role="STAFF",
        )

        user.set_password(
            raw_password
        )

        user.save()

        # ----------------------------------------------------
        # STAFF
        # ----------------------------------------------------

        staff = Staff.objects.create(
            user=user,
            staff_name=staff_name,
            staff_id=staff_id,
        )

        print(
            "STAFF CREATED:",
            staff.id,
            staff.staff_id,
            staff.staff_name,
        )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        created_staff.append({
            "staff_id": staff.staff_id,
            "staff_name": staff.staff_name,
            "username": username,
            "temporary_password": raw_password,
        })

    # ========================================================
    # RETURN
    # ========================================================

    return {
        "created_staff": created_staff,
        "ignored_staff": ignored_staff,
        "failed_staff": failed_staff,
    }