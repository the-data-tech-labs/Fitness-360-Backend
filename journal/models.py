from django.db import models
from django.contrib.auth.models import User

class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link entries to a user
    date = models.DateField(auto_now_add=True)  # Automatically set the date when created
    mood = models.CharField(max_length=20)  # Store the mood (e.g., "happy", "neutral", "sad")
    notes = models.TextField()  # Store the journal entry text

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.mood}"