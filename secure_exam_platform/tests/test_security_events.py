from django.test import TestCase
from apps.users.models import User
from apps.exams.models import Exam, ExamSession
from apps.monitoring.models import SecurityEvent


class SecurityEventTests(TestCase):
    def test_security_event_storage(self):
        user = User.objects.create_user(username='student3', password='pwd')
        exam = Exam.objects.create(title='Sec', duration_minutes=30)
        session = ExamSession.objects.create(student=user, exam=exam)
        event = SecurityEvent.objects.create(session=session, event_type='fullscreen_exit', severity='high', metadata={'x': 1})
        self.assertEqual(event.metadata['x'], 1)
