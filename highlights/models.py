# highlights/models.py

from django.db import models
from django.contrib.auth.models import User

class Highlight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fitness_highlights = models.TextField()
    nutrition_highlights = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Highlights for {self.user.username} - {self.created_at.date()}"
