from rest_framework import serializers
from .models import SecurityEvent, ProctorSnapshot


class SecurityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvent
        fields = '__all__'


class ProctorSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProctorSnapshot
        fields = '__all__'
