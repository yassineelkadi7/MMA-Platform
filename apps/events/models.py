"""
Events app models — WeightClass, Fighter, Event, Fight.
"""
from django.db import models


class WeightClass(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g. "Lightweight"
    limit_kg = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} (≤ {self.limit_kg} kg)"


class Fighter(models.Model):
    external_id = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=200, db_index=True)
    nationality = models.CharField(max_length=100)
    weight_class = models.ForeignKey(
        WeightClass, on_delete=models.SET_NULL, null=True
    )
    fighting_style = models.CharField(max_length=100, blank=True)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    draws = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class Event(models.Model):
    STATUS_CHOICES = [
        ("upcoming", "Upcoming"),
        ("live", "Live"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    external_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=300)
    date = models.DateTimeField(db_index=True)
    location = models.CharField(max_length=300)
    venue = models.CharField(max_length=300, blank=True)
    broadcast_info = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="upcoming"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.date:%Y-%m-%d})"


class Fight(models.Model):
    METHOD_CHOICES = [
        ("ko", "KO/TKO"),
        ("sub", "Submission"),
        ("dec", "Decision"),
        ("dq", "DQ"),
        ("other", "Other"),
    ]
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="fights"
    )
    fighter_a = models.ForeignKey(
        Fighter, on_delete=models.CASCADE, related_name="fights_as_a"
    )
    fighter_b = models.ForeignKey(
        Fighter, on_delete=models.CASCADE, related_name="fights_as_b"
    )
    winner = models.ForeignKey(
        Fighter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wins_set",
    )
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, blank=True)
    is_main_event = models.BooleanField(default=False)
    bout_order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.fighter_a} vs {self.fighter_b} @ {self.event}"
