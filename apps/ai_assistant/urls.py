"""
AI Assistant app URL configuration.
"""
from django.urls import path

from apps.ai_assistant.views import (
    ChatView,
    GenerateProgramView,
    ProgramDownloadView,
    ProgramListView,
)

app_name = "ai_assistant"

urlpatterns = [
    path("chat/", ChatView.as_view(), name="chat"),
    path("generate-program/", GenerateProgramView.as_view(), name="generate_program"),
    path("programs/", ProgramListView.as_view(), name="program_list"),
    path("programs/<int:pk>/download/", ProgramDownloadView.as_view(), name="program_download"),
]
