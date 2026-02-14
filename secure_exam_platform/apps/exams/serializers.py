from rest_framework import serializers
from .models import Exam, Question, Choice, ExamSession, Answer, Result, Warning


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'prompt', 'question_type', 'points', 'choices']

    def get_choices(self, obj):
        choices = list(obj.choices.all().order_by('order'))
        import random
        random.shuffle(choices)
        return ChoiceSerializer(choices, many=True).data


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'


class ExamSessionSerializer(serializers.ModelSerializer):
    remaining_seconds = serializers.SerializerMethodField()

    class Meta:
        model = ExamSession
        fields = '__all__'
        read_only_fields = ['student', 'partial_score', 'start_time', 'violations_count']

    def get_remaining_seconds(self, obj):
        return obj.remaining_seconds()


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class WarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warning
        fields = '__all__'


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'
