from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Exam, Question, ExamSession, Answer, Result
from .serializers import ExamSerializer, QuestionSerializer, ExamSessionSerializer, AnswerSerializer, ResultSerializer
from apps.monitoring.models import SecurityEvent
from apps.monitoring.tasks import auto_submit_session_task


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exam.objects.filter(is_active=True)
    serializer_class = ExamSerializer


class ExamSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSessionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_exam_admin:
            return ExamSession.objects.select_related('exam', 'student')
        return ExamSession.objects.filter(student=user).select_related('exam')

    @transaction.atomic
    @action(detail=False, methods=['post'])
    def start(self, request):
        exam = get_object_or_404(Exam, pk=request.data.get('exam_id'), is_active=True)
        if exam.webcam_required and not request.data.get('webcam_active'):
            return Response({'detail': 'Webcam obligatoire.'}, status=400)
        session = ExamSession(student=request.user, exam=exam, webcam_active=True, fullscreen_status=True)
        session.randomize_questions()
        session.save()
        auto_submit_session_task.apply_async((session.id,), countdown=exam.duration_minutes * 60)
        return Response(self.get_serializer(session).data, status=201)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        session = self.get_object()
        grade_session(session, forced=False)
        return Response({'status': 'submitted'})

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        session = self.get_object()
        session.forced_closed = True
        session.status = 'closed'
        session.end_time = timezone.now()
        session.save(update_fields=['forced_closed', 'status', 'end_time'])
        grade_session(session, forced=True)
        return Response({'status': 'closed'})


class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answer.objects.filter(session__student=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_questions(request, session_id):
    session = get_object_or_404(ExamSession, id=session_id, student=request.user)
    if not session.randomized_question_ids:
        session.randomize_questions()
        session.save(update_fields=['randomized_question_ids'])
    qs = Question.objects.filter(id__in=session.randomized_question_ids)
    ordered = sorted(list(qs), key=lambda q: session.randomized_question_ids.index(q.id))
    return Response(QuestionSerializer(ordered, many=True).data)


def grade_session(session, forced=False):
    total_points = 0.0
    earned = 0.0
    for answer in session.answers.select_related('question', 'selected_choice'):
        q = answer.question
        total_points += q.points
        if q.question_type == Question.QuestionType.MCQ:
            answer.is_correct = bool(answer.selected_choice and answer.selected_choice.is_correct)
        else:
            answer.is_correct = answer.text_answer.strip().lower() == q.expected_answer.strip().lower()
        answer.score = q.points if answer.is_correct else 0.0
        earned += answer.score
        answer.save(update_fields=['is_correct', 'score'])

    percentage = (earned / total_points * 100) if total_points else 0.0
    session.partial_score = earned
    session.auto_submitted = forced or session.auto_submitted
    session.status = 'submitted'
    session.end_time = session.end_time or timezone.now()
    session.save(update_fields=['partial_score', 'auto_submitted', 'status', 'end_time'])
    Result.objects.update_or_create(session=session, defaults={'final_score': earned, 'percentage': percentage})
    SecurityEvent.objects.create(
        session=session,
        event_type='auto_submit' if forced else 'manual_submit',
        severity='high' if forced else 'medium',
        metadata={'final_score': earned, 'percentage': percentage},
    )


def student_exam_page(request, session_id):
    return render(request, 'student/exam_room.html', {'session_id': session_id})


def admin_dashboard(request):
    return render(request, 'admin_dashboard/live_dashboard.html')
