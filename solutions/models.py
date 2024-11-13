from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="log_records"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    data = models.JSONField()
