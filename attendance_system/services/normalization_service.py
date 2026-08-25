import re
import unicodedata
from difflib import SequenceMatcher

import numpy as np
import pandas as pd


# ============================================================
# GENERAL TEXT
# ============================================================

def clean_text(value):
    if value is None:
        return ""

    if isinstance(value, (float, np.floating)) and np.isnan(value):
        return ""

    if isinstance(value, pd.Series):
        raise TypeError(
            "clean_text() expects a single value, not a Pandas Series."
        )

    value = unicodedata.normalize("NFKC", str(value))
    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)

    return value


def compact_text(value):
    return re.sub(
        r"[^a-z0-9]",
        "",
        clean_text(value)
    )

# ============================================================
# STAFF FIELD DETECTION
# ============================================================

STAFF_NAME_ALIASES = {
    "staffname",
    "teachername",
    "professorname",
    "profname",
    "facultyname",
    "lecturername",
    "instructorname",
    "educatorname",
    "employeename",
    "stafffullname",
    "teacherfullname",
    "facultyfullname",

    # Generic
    "name",
}


STAFF_ID_ALIASES = {
    "staffid",
    "staffno",
    "staffnumber",

    "teacherid",
    "teacherno",
    "teachernumber",

    "professorid",
    "professorno",
    "professornumber",

    "facultyid",
    "facultyno",
    "facultynumber",

    "lecturerid",
    "lecturerno",
    "lecturernumber",

    "instructorid",
    "instructorno",
    "instructornumber",

    "employeeid",
    "employeeno",
    "employeenumber",
    "employeeidentifier",
}


STAFF_FIELD_MAP = {
    **{
        alias: "staff_name"
        for alias in STAFF_NAME_ALIASES
    },
    **{
        alias: "staff_id"
        for alias in STAFF_ID_ALIASES
    },
}


def detect_staff_field(header):
    """
    Detect staff columns from arbitrary XLSX/CSV/PDF headers.

    Examples:

        Staff Name       -> staff_name
        Teacher Name     -> staff_name
        Professor Name   -> staff_name
        Faculty Name     -> staff_name
        Lecturer Name    -> staff_name
        Employee Name    -> staff_name
        Name             -> staff_name

        Staff ID         -> staff_id
        Teacher ID       -> staff_id
        Professor ID     -> staff_id
        Faculty ID       -> staff_id
        Employee Number  -> staff_id
    """

    normalized = compact_text(header)

    if not normalized:
        return None

    return STAFF_FIELD_MAP.get(
        normalized
    )
# ============================================================
# REQUIRED FIELDS
# ============================================================

REQUIRED_FIELDS = {
    "register_no",
    "student_name",
    "class_name",
    "batch",
}


# ============================================================
# HEADER DETECTION
# ============================================================

EXACT_FIELD_MAP = {

    # Register number
    "reg": "register_no",
    "regno": "register_no",
    "regnum": "register_no",
    "regnumber": "register_no",

    "registernumber": "register_no",
    "registernum": "register_no",

    "registrationno": "register_no",
    "registrationnum": "register_no",
    "registrationnumber": "register_no",

    "studentid": "register_no",
    "studentno": "register_no",
    "studentnumber": "register_no",

    "admissionid": "register_no",
    "admissionno": "register_no",
    "admissionnumber": "register_no",

    # Student name
    "name": "student_name",
    "studentname": "student_name",
    "studentfullname": "student_name",
    "fullname": "student_name",
    "candidatename": "student_name",

    # Class
    "class": "class_name",
    "classname": "class_name",
    "classsection": "class_name",
    "section": "class_name",
    "academicclass": "class_name",

    # Batch
    "batch": "batch",
    "batchname": "batch",
    "batchyear": "batch",
    "academicbatch": "batch",
    "academicyear": "batch",
}


FIELD_REFERENCE_NAMES = {

    "register_no": (
        "reg",
        "reg no",
        "reg number",
        "register no",
        "register number",
        "registration no",
        "registration number",
    ),

    "student_name": (
        "name",
        "student name",
        "student full name",
        "full name",
        "candidate name",
    ),

    "class_name": (
        "class",
        "class name",
        "class section",
        "academic class",
        "section",
    ),

    "batch": (
        "batch",
        "batch name",
        "batch year",
        "academic batch",
        "academic year",
    ),
}


def detect_field(header):
    compact = compact_text(header)

    if not compact:
        return None

    return EXACT_FIELD_MAP.get(compact)


def similarity(a, b):
    a = compact_text(a)
    b = compact_text(b)
    if not a or not b:
        return 0.0

    return SequenceMatcher(
        None,
        a,
        b
    ).ratio()


def fuzzy_detect_field(header, threshold=0.82):
    detected = detect_field(header)
    if detected:
        return detected
    best_field = None
    best_score = 0.0
    for field, references in FIELD_REFERENCE_NAMES.items():
        for reference in references:
            score = similarity(
                header,
                reference
            )

            if score > best_score:
                best_score = score
                best_field = field
    if best_score >= threshold:
        return best_field

    return None


def map_columns(columns):

    mapping = {}

    for column in columns:

        field = fuzzy_detect_field(column)

        if not field:
            continue

        # Never allow two input columns to map
        # to the same canonical field.
        if field in mapping.values():
            continue

        mapping[column] = field

    missing = REQUIRED_FIELDS - set(mapping.values())

    if missing:
        raise ValueError(
            "Required columns missing: "
            + ", ".join(sorted(missing))
        )

    return mapping


# ============================================================
# REGISTER NUMBER
# ============================================================

def _normalize_register(value):

    if value is None:
        return ""

    if isinstance(value, (float, np.floating)) and np.isnan(value):
        return ""

    value = unicodedata.normalize(
        "NFKC",
        str(value)
    )

    value = value.strip()

    # Excel numeric conversion:
    # 2023001.0 -> 2023001
    if value.endswith(".0"):
        value = value[:-2]

    # 2023 001 -> 2023001
    value = re.sub(
        r"\s+",
        "",
        value
    )

    return value.upper()


def normalize_register_no(value):

    if isinstance(value, pd.Series):
        return value.map(_normalize_register)

    return _normalize_register(value)


# ============================================================
# STUDENT NAME
# ============================================================

def _normalize_name(value):

    if value is None:
        return ""

    if isinstance(value, (float, np.floating)) and np.isnan(value):
        return ""

    value = unicodedata.normalize(
        "NFKC",
        str(value)
    )

    value = " ".join(
        value.strip().split()
    )

    if not value:
        return ""

    return value.title()


def normalize_student_name(value):

    if isinstance(value, pd.Series):
        return value.map(_normalize_name)

    return _normalize_name(value)


# ============================================================
# CLASS
# ============================================================

YEAR_MAPPING = {
    "first": "I",
    "1st": "I",
    "one": "I",
    "i": "I",

    "second": "II",
    "2nd": "II",
    "two": "II",
    "ii": "II",

    "third": "III",
    "3rd": "III",
    "three": "III",
    "iii": "III",

    "fourth": "IV",
    "4th": "IV",
    "four": "IV",
    "iv": "IV",
}


DEPARTMENT_ALIASES = {

    "informationtechnology": "IT",
    "informationtech": "IT",
    "information": "IT",
    "technology": "IT",
    "it": "IT",

    "computerscienceengineering": "CSE",
    "computerscience": "CSE",
    "computerengineering": "CSE",
    "cse": "CSE",

    "electronicscommunication": "ECE",
    "electronicsandcommunication": "ECE",
    "electronics": "ECE",
    "ece": "ECE",

    "electricalandelectronics": "EEE",
    "electrical": "EEE",
    "eee": "EEE",

    "mechanicalengineering": "MECH",
    "mechanical": "MECH",
    "mech": "MECH",

    "civilengineering": "CIVIL",
    "civil": "CIVIL",

    "artificialintelligence": "AI",
    "aiml": "AIML",
    "aids": "AIDS",
    "ai": "AI",
}


def _normalize_class(value):

    if value is None:
        return ""

    if isinstance(value, (float, np.floating)) and np.isnan(value):
        return ""

    value = unicodedata.normalize(
        "NFKC",
        str(value)
    )

    value = value.strip()

    if not value:
        return ""

    # Second-Year/IT-A
    # II-IT-A
    # II/IT/A
    value = re.sub(
        r"[-_/]+",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    tokens = value.lower().split()

    year = None
    department = None
    section = None

    # Year
    for token in tokens:

        token = token.strip(
            ".,()[]{}"
        )

        if token in YEAR_MAPPING:
            year = YEAR_MAPPING[token]
            break

    # Department
    compact = "".join(tokens)

    for alias, canonical in sorted(
        DEPARTMENT_ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):

        if alias in compact:
            department = canonical
            break

    # Section
    match = re.search(
        r"\b([A-D])\b",
        value,
        re.IGNORECASE
    )

    if match:
        section = match.group(1).upper()

    if year and department and section:
        return f"{year} {department} {section}"

    # Do not guess incomplete class names.
    return " ".join(
        token.upper()
        for token in tokens
    )


def normalize_class_name(value):

    if isinstance(value, pd.Series):
        return value.map(_normalize_class)

    return _normalize_class(value)


# ============================================================
# BATCH
# ============================================================

def _normalize_batch(value):

    if value is None:
        return ""

    if isinstance(value, (float, np.floating)) and np.isnan(value):
        return ""

    value = unicodedata.normalize(
        "NFKC",
        str(value)
    )

    value = value.strip()

    if not value:
        return ""

    value = re.sub(
        r"\s+",
        "",
        value
    )

    value = value.replace("/", "-")
    value = value.replace("_", "-")

    # 2023-2027
    match = re.fullmatch(
        r"(20\d{2})-(20\d{2})",
        value
    )

    if match:

        return (
            f"{int(match.group(1)):04d}-"
            f"{int(match.group(2)):04d}"
        )

    # 23-27 -> 2023-2027
    match = re.fullmatch(
        r"(\d{2})-(\d{2})",
        value
    )

    if match:

        start = int(match.group(1))
        end = int(match.group(2))

        start_year = 2000 + start

        if end >= start:
            end_year = 2000 + end
        else:
            end_year = 2100 + end

        return f"{start_year:04d}-{end_year:04d}"

    # Unknown format is preserved rather than guessed.
    return value


def normalize_batch(value):

    if isinstance(value, pd.Series):
        return value.map(_normalize_batch)

    return _normalize_batch(value)


# ============================================================
# RECORD NORMALIZATION
# ============================================================

def normalize_student_record(record):

    return {
        "register_no": normalize_register_no(
            record.get("register_no")
        ),

        "student_name": normalize_student_name(
            record.get("student_name")
        ),

        "class_name": normalize_class_name(
            record.get("class_name")
        ),

        "batch": normalize_batch(
            record.get("batch")
        ),

        "_sheet": record.get("_sheet"),
        "_row": record.get("_row"),
    }

# ============================================================
# STAFF HEADER ALIASES
# ============================================================

STAFF_NAME_ALIASES = {
    "staffname",
    "teachername",
    "professorname",
    "profname",
    "facultyname",
    "lecturername",
    "instructorname",
    "educatorname",
    "employeename",
    "fullname",
    "stafffullname",
    "teacherfullname",
    "facultyfullname",
    "name",
}

STAFF_ID_ALIASES = {
    "staffid",
    "staffno",
    "staffnumber",

    "teacherid",
    "teacherno",
    "teachernumber",

    "professorid",
    "professorno",
    "professornumber",

    "facultyid",
    "facultyno",
    "facultynumber",

    "lecturerid",
    "lecturerno",
    "lecturernumber",

    "instructorid",
    "instructorno",
    "instructornumber",

    "employeeid",
    "employeeno",
    "employeenumber",
    "employeeidentifier",
}


def compact_text(value):
    """
    Convert a header into a comparison key.

    Staff Name -> staffname
    Staff_Name -> staffname
    Staff-ID -> staffid
    Employee ID -> employeeid
    """

    if value is None:
        return ""

    if isinstance(
        value,
        (float, np.floating),
    ) and np.isnan(value):
        return ""

    value = unicodedata.normalize(
        "NFKC",
        str(value),
    )

    value = value.strip().lower()

    return re.sub(
        r"[^a-z0-9]",
        "",
        value,
    )


# ============================================================
# STAFF FIELD DETECTION
# ============================================================

def detect_staff_field(header):

    normalized = compact_text(header)

    if not normalized:
        return None

    if normalized in STAFF_NAME_ALIASES:
        return "staff_name"

    if normalized in STAFF_ID_ALIASES:
        return "staff_id"

    return None


# ============================================================
# STAFF NAME
# ============================================================

def _normalize_staff_name(value):

    if value is None:
        return ""

    if isinstance(
        value,
        (float, np.floating),
    ) and np.isnan(value):
        return ""

    value = unicodedata.normalize(
        "NFKC",
        str(value),
    )

    value = " ".join(
        value.strip().split()
    )

    if not value:
        return ""

    return value.title()


def normalize_staff_name(value):

    if isinstance(value, pd.Series):
        return value.map(
            _normalize_staff_name
        )

    return _normalize_staff_name(value)


# ============================================================
# STAFF ID
# ============================================================

def _normalize_staff_id(value):

    if value is None:
        return ""

    if isinstance(
        value,
        (float, np.floating),
    ) and np.isnan(value):
        return ""

    value = unicodedata.normalize(
        "NFKC",
        str(value),
    )

    value = value.strip()

    if not value:
        return ""

    # Excel numeric value:
    # 123.0 -> 123
    if value.endswith(".0"):
        value = value[:-2]

    # STF 001 -> STF001
    value = re.sub(
        r"\s+",
        "",
        value,
    )

    return value.upper()


def normalize_staff_id(value):

    if isinstance(value, pd.Series):
        return value.map(
            _normalize_staff_id
        )

    return _normalize_staff_id(value)