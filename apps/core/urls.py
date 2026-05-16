"""
Core app URL configuration.
"""
from django.urls import path
from . import views
from .admin_views import APIMonitorDashboardView

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("admin/api-monitor/", APIMonitorDashboardView.as_view(), name="api_monitor"),
]
