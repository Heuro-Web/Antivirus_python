import random
from django.conf import settings
from django.db import models
from django.utils import timezone


class Exam(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=60)
    max_violations = models.PositiveIntegerField(default=5)
    webcam_required = models.BooleanField(default=True)
    screen_capture_allowed = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)


class Question(models.Model):
    class QuestionType(models.TextChoices):
        MCQ = 'mcq', 'QCM'
        SHORT = 'short', 'Réponse courte'
        CODE = 'code', 'Code'

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    prompt = models.TextField()
    question_type = models.CharField(max_length=20, choices=QuestionType.choices)
    points = models.FloatField(default=1.0)
    order = models.PositiveIntegerField(default=0)
    expected_answer = models.TextField(blank=True)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)


class ExamSession(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exam_sessions')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(blank=True, null=True)
    last_activity = models.DateTimeField(default=timezone.now)
    violations_count = models.PositiveIntegerField(default=0)
    webcam_active = models.BooleanField(default=False)
    fullscreen_status = models.BooleanField(default=False)
    tab_switch_count = models.PositiveIntegerField(default=0)
    forced_closed = models.BooleanField(default=False)
    auto_submitted = models.BooleanField(default=False)
    partial_score = models.FloatField(default=0.0)
    randomized_question_ids = models.JSONField(default=list)
    status = models.CharField(max_length=20, default='active')

    def remaining_seconds(self):
        delta = timezone.now() - self.start_time
        total = self.exam.duration_minutes * 60
        return max(total - int(delta.total_seconds()), 0)

    def randomize_questions(self):
        ids = list(self.exam.questions.values_list('id', flat=True))
        random.shuffle(ids)
        self.randomized_question_ids = ids


class Answer(models.Model):
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
    text_answer = models.TextField(blank=True)
    code_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    score = models.FloatField(default=0.0)
    submitted_at = models.DateTimeField(auto_now=True)


class Warning(models.Model):
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='warnings')
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)


class Result(models.Model):
    session = models.OneToOneField(ExamSession, on_delete=models.CASCADE, related_name='result')
    final_score = models.FloatField(default=0.0)
    percentage = models.FloatField(default=0.0)
    graded_at = models.DateTimeField(auto_now=True)
