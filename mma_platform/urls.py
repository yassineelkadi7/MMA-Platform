"""
URL configuration for mma_platform project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # App URL includes
    path("accounts/", include("apps.accounts.urls")),
    path("news/", include("apps.news.urls")),
    path("events/", include("apps.events.urls")),
    path("training/", include("apps.training.urls")),
    path("ai/", include("apps.ai_assistant.urls")),

    # Home page (served by core app)
    path("", include("apps.core.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = "apps.core.views.handler404"
handler500 = "apps.core.views.handler500"
