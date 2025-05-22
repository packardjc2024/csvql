# myapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ApprovedEmail
from django.core.mail import EmailMessage
from django.conf import settings
