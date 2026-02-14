from django.test import TestCase
from django.utils import timezone
from apps.users.models import User
from apps.exams.models import Exam, Question, ExamSession


class ExamSessionModelTests(TestCase):
    def test_remaining_seconds_non_negative(self):
        user = User.objects.create_user(username='student', password='pwd')
        exam = Exam.objects.create(title='Math', duration_minutes=1)
        session = ExamSession.objects.create(student=user, exam=exam, start_time=timezone.now())
        self.assertGreaterEqual(session.remaining_seconds(), 0)

    def test_randomization(self):
        user = User.objects.create_user(username='student2', password='pwd')
        exam = Exam.objects.create(title='Algo', duration_minutes=10)
        q1 = Question.objects.create(exam=exam, prompt='Q1', question_type='short')
        q2 = Question.objects.create(exam=exam, prompt='Q2', question_type='short')
        session = ExamSession.objects.create(student=user, exam=exam)
        session.randomize_questions()
        self.assertCountEqual(session.randomized_question_ids, [q1.id, q2.id])
