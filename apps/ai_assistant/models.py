"""
AI Assistant app models — ConversationMessage, TrainingProgram.
"""
from django.db import models


class ConversationMessage(models.Model):
    ROLE_CHOICES = [("user", "User"), ("assistant", "Assistant")]
    session_key = models.CharField(max_length=40, db_index=True)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["session_key", "created_at"])]


class TrainingProgram(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="training_programs",
    )
    title = models.CharField(max_length=300)
    latex_source = models.TextField()
    pdf_file = models.FileField(upload_to="training_programs/")
    generated_at = models.DateTimeField(auto_now_add=True)
    parameters = models.JSONField(default=dict)

    class Meta:
        ordering = ["-generated_at"]
