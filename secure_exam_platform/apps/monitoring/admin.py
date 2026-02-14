from django.contrib import admin
from .models import SecurityEvent, ProctorSnapshot

admin.site.register([SecurityEvent, ProctorSnapshot])
