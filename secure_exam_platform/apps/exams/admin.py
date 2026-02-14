from django.contrib import admin
from .models import Exam, Question, Choice, ExamSession, Answer, Warning, Result

admin.site.register([Exam, Question, Choice, ExamSession, Answer, Warning, Result])
