from rest_framework import serializers
from .models import CommunityPost, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at']

class CommunityPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    total_likes = serializers.SerializerMethodField()

    class Meta:
        model = CommunityPost
        fields = ['id', 'user', 'text', 'image', 'video', 'category', 'created_at', 'updated_at', 'comments', 'likes', 'total_likes']

    def get_total_likes(self, obj):
        return obj.total_likes()  # Call the method on the CommunityPost model to get total likes
