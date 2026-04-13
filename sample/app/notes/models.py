"""
Notes app models.

A simple Note model for demonstrating Django REST API with PostgreSQL.
Intentionally kept minimal so the tutorial focuses on deployment, not Django code.
"""

from django.db import models


class Note(models.Model):
    """A simple note with title, body, and timestamps."""

    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
