"""
Training app URL configuration.
"""
from django.urls import path
from .views import TrainingView

app_name = "training"

urlpatterns = [
    path("", TrainingView.as_view(), name="stopwatch"),
]
