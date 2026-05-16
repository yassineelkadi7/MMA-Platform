"""
News app models — Article.
"""
from django.db import models


class Article(models.Model):
    CATEGORY_CHOICES = [
        ("general", "General MMA"),
        ("fighter", "Fighter News"),
        ("preview", "Event Previews"),
        ("results", "Fight Results"),
    ]
    external_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=500)
    summary = models.TextField()
    source_name = models.CharField(max_length=200)
    source_url = models.URLField()
    image_url = models.URLField(blank=True, default="")  # article thumbnail from API
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    published_at = models.DateTimeField(db_index=True)
    fetched_at = models.DateTimeField(auto_now=True)
    is_hidden = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-published_at"]
        indexes = [models.Index(fields=["category", "-published_at"])]

    def __str__(self):
        return self.title
