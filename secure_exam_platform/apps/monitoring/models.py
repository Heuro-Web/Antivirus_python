from django.db import models
from apps.exams.models import ExamSession


class SecurityEvent(models.Model):
    class Severity(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='security_events')
    event_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM)
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)


class ProctorSnapshot(models.Model):
    class SnapshotType(models.TextChoices):
        WEBCAM = 'webcam', 'Webcam'
        SCREEN = 'screen', 'Screen'

    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='snapshots')
    snapshot_type = models.CharField(max_length=20, choices=SnapshotType.choices)
    image = models.TextField(help_text='Base64 payload or storage pointer')
    created_at = models.DateTimeField(auto_now_add=True)
