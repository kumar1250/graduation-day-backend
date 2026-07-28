import openpyxl
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STUDENTS_FILE = os.path.join(BASE_DIR, "data", "students.xlsx")
REGISTRATIONS_FILE = os.path.join(BASE_DIR, "data", "registrations.xlsx")

# Column order in students.xlsx:
# Slno, Roll Number, Student Name, Father Name, Class Awarded, CGPA, Month & Year, Mobile, Email
STUDENT_FIELDS = [
    "slno", "roll_no", "name", "father_name", "class_awarded",
    "cgpa", "month_year", "mobile", "email",
]


def _row_to_student(row):
    return dict(zip(STUDENT_FIELDS, row))


def find_student(roll_no):
    wb = openpyxl.load_workbook(STUDENTS_FILE, data_only=True)
    ws = wb.active
    roll_no = roll_no.strip().upper()
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[1] and str(row[1]).strip().upper() == roll_no:
            return _row_to_student(row)
    return None


def get_all_students(search=None):
    wb = openpyxl.load_workbook(STUDENTS_FILE, data_only=True)
    ws = wb.active
    students = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[1]:
            continue
        student = _row_to_student(row)
        if search:
            s = search.strip().lower()
            haystack = f"{student['roll_no']} {student['name']} {student['father_name']}".lower()
            if s not in haystack:
                continue
        students.append(student)
    return students


def is_already_registered(roll_no):
    wb = openpyxl.load_workbook(REGISTRATIONS_FILE)
    ws = wb.active
    roll_no = roll_no.strip().upper()
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] and str(row[0]).strip().upper() == roll_no:
            return True
    return False


def save_registration(data):
    persons = data.get("persons_list", [])
    names = ", ".join(p.get("name", "") for p in persons)
    contacts = ", ".join(p.get("contact", "") for p in persons)
    relations = ", ".join(p.get("relation", "") for p in persons)

    wb = openpyxl.load_workbook(REGISTRATIONS_FILE)
    ws = wb.active
    ws.append([
        data["roll_no"], data.get("name", ""), data.get("attend", ""), len(persons),
        names, contacts, relations,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ])

    try:
        wb.save(REGISTRATIONS_FILE)
    except PermissionError:
        raise PermissionError(
            "registrations.xlsx is open elsewhere (Excel or OneDrive sync). Please close it and try again."
        )


def get_all_registrations():
    wb = openpyxl.load_workbook(REGISTRATIONS_FILE)
    ws = wb.active
    results = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]:
            continue
        names = [n.strip() for n in (row[4] or "").split(",") if n.strip()]
        contacts = [c.strip() for c in (row[5] or "").split(",") if c.strip()]
        relations = [r.strip() for r in (row[6] or "").split(",") if r.strip()]
        persons = list(zip(names, contacts, relations))
        results.append({
            "roll_no": row[0], "name": row[1], "attend": row[2],
            "persons_count": row[3], "persons": persons,
            "submitted_at": row[7],
        })
    return results
