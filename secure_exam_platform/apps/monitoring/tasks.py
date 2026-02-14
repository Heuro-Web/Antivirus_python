from celery import shared_task
from django.utils import timezone
from apps.exams.models import ExamSession
from apps.exams.views import grade_session
from .models import SecurityEvent


@shared_task
def auto_submit_session_task(session_id):
    try:
        session = ExamSession.objects.get(id=session_id, status='active')
    except ExamSession.DoesNotExist:
        return

    session.auto_submitted = True
    session.end_time = timezone.now()
    session.save(update_fields=['auto_submitted', 'end_time'])
    grade_session(session, forced=True)
    SecurityEvent.objects.create(session=session, event_type='timer_expired', severity='critical', metadata={})
