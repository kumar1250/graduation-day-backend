from django.urls import path
from . import views

urlpatterns = [
    path("student/<str:roll_no>/", views.lookup_student),
    path("students/", views.list_students),
    path("submit/", views.submit_registration),
    path("dashboard/", views.dashboard),
    path("registrations/", views.list_registrations),
    path("download/registrations/", views.download_registrations),
    path("download/students/", views.download_students),
]
