from django.db import models
from django.contrib.sessions.models import Session

class Document(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, default=None, null=True)
    document = models.FileField(upload_to='documents')