from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

def validate_image_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5 MB
        raise ValidationError("The maximum file size for images is 5 MB.")

def validate_video_size(value):
    filesize = value.size
    if filesize > 50 * 1024 * 1024:  # 50 MB
        raise ValidationError("The maximum file size for videos is 50 MB.")

class CommunityPost(models.Model):
    CATEGORY_CHOICES = [
        ('fitness', 'Fitness'),
        ('nutrition', 'Nutrition'),
        ('yoga', 'Yoga'),
        ('mental_health', 'Mental Health'),
        ('recipes', 'Recipes'),
        ('motivation', 'Motivation'),
        ("qna","QnA"),
        ("challenges","Challenges"),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='fitness')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(
        upload_to='community_images/',
        null=True,
        blank=True,
        validators=[validate_image_size]
    )
    video = models.FileField(
        upload_to='community_videos/',
        null=True,
        blank=True,
        validators=[validate_video_size]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def _str_(self):
        return f"Post by {self.user.username} at {self.created_at}"

    def total_likes(self):
        return self.likes.count()

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(CommunityPost, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Comment by {self.user.username} on {self.post.id}"
