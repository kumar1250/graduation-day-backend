from django.http import FileResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . import excel_utils


@api_view(["GET"])
def lookup_student(request, roll_no):
    student = excel_utils.find_student(roll_no)
    if not student:
        return Response({"error": "Student not found"}, status=404)
    student["already_registered"] = excel_utils.is_already_registered(roll_no)
    return Response(student)


@api_view(["GET"])
def list_students(request):
    search = request.query_params.get("search")
    students = excel_utils.get_all_students(search=search)
    return Response({"count": len(students), "students": students})


@api_view(["POST"])
def submit_registration(request):
    data = request.data
    roll_no = data.get("roll_no")

    if not roll_no:
        return Response({"error": "Roll number required"}, status=400)
    if not excel_utils.find_student(roll_no):
        return Response({"error": "Student not found"}, status=404)
    if excel_utils.is_already_registered(roll_no):
        return Response({"error": "Already registered"}, status=400)

    try:
        excel_utils.save_registration(data)
    except PermissionError as e:
        return Response({"error": str(e)}, status=503)

    return Response({"message": "Registration successful"})


@api_view(["GET"])
def dashboard(request):
    students = excel_utils.get_all_students()
    regs = excel_utils.get_all_registrations()
    yes = sum(1 for r in regs if r["attend"] == "Yes")
    no = sum(1 for r in regs if r["attend"] == "No")
    total_persons = sum(r["persons_count"] or 0 for r in regs)
    return Response({
        "total_students": len(students),
        "total_registered": len(regs),
        "yes": yes,
        "no": no,
        "total_accompanying": total_persons,
        "not_yet_registered": len(students) - len(regs),
    })


@api_view(["GET"])
def list_registrations(request):
    regs = excel_utils.get_all_registrations()
    return Response(regs)


@api_view(["GET"])
def download_registrations(request):
    return FileResponse(
        excel_utils.export_registrations_xlsx_bytes(),
        as_attachment=True,
        filename="registrations.xlsx",
    )


@api_view(["GET"])
def download_students(request):
    return FileResponse(
        excel_utils.export_students_xlsx_bytes(),
        as_attachment=True,
        filename="students.xlsx",
    )
