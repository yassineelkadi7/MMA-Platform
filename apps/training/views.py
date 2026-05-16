"""
Training app views — stopwatch page.
"""
from django.views.generic import TemplateView


class TrainingView(TemplateView):
    template_name = "training/stopwatch.html"
