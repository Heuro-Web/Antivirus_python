from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamViewSet, ExamSessionViewSet, AnswerViewSet, session_questions

router = DefaultRouter()
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'sessions', ExamSessionViewSet, basename='session')
router.register(r'answers', AnswerViewSet, basename='answer')

urlpatterns = [
    path('', include(router.urls)),
    path('sessions/<int:session_id>/questions/', session_questions, name='session-questions'),
]
