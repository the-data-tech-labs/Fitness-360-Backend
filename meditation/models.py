from django.db import models

class DailyExperience(models.Model):
    experience_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Experience on {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class MeditationRecommendation(models.Model):
    experience = models.ForeignKey(DailyExperience, on_delete=models.CASCADE, related_name='recommendations')
    meditation_type = models.CharField(max_length=100)
    duration_minutes = models.IntegerField()
    how_to_perform = models.TextField()
    benefits = models.TextField()
    
    def __str__(self):
        return f"{self.meditation_type} for {self.experience}"