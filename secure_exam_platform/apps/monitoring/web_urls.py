from django.urls import path
from apps.exams.views import student_exam_page, admin_dashboard

urlpatterns = [
    path('exam/<int:session_id>/', student_exam_page, name='student-exam-room'),
    path('dashboard/admin/live/', admin_dashboard, name='admin-live-dashboard'),
]
