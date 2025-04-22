from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from .models import CommunityPost, Comment
from .serializers import CommunityPostSerializer, CommentSerializer

# File Size Validation
def validate_file_size(file, max_size):
    if file.size > max_size:
        raise ValidationError(f"The maximum file size is {max_size / 1024 / 1024} MB.")

# Community Post List and Create View
class CommunityPostListCreateView(generics.ListCreateAPIView):
    queryset = CommunityPost.objects.all()
    serializer_class = CommunityPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']  # Allow filtering by category

    def perform_create(self, serializer):
        image = self.request.FILES.get('image')
        video = self.request.FILES.get('video')

        # Validate file size
        if image:
            validate_file_size(image, 5 * 1024 * 1024)  # 5 MB max size
        if video:
            validate_file_size(video, 50 * 1024 * 1024)  # 50 MB max size

        serializer.save(user=self.request.user)  # Save post with the logged-in user

# Community Post Retrieve, Update, and Destroy View
class CommunityPostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CommunityPost.objects.all()
    serializer_class = CommunityPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        post = self.get_object()
        if post.user != self.request.user:  # Ensure the post owner is the user making the request
            raise PermissionDenied("You do not have permission to edit this post.")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:  # Ensure the post owner is the user making the request
            raise PermissionDenied("You do not have permission to delete this post.")
        instance.delete()

from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from .models import Comment, CommunityPost
from .serializers import CommentSerializer

# Custom permission for update/delete actions
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

# Comment Create and List View
class CommentCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]  # Anyone can read comments
        return [permissions.IsAuthenticated()]  # Only authenticated users can post

    def get_queryset(self):
        """Return only comments for the requested post."""
        post_id = self.kwargs.get("post_id")
        post = get_object_or_404(CommunityPost, id=post_id)  # Ensure post exists
        return Comment.objects.filter(post=post).order_by("-created_at")

    def perform_create(self, serializer):
        """Assign user and post when creating a comment."""
        post = get_object_or_404(CommunityPost, id=self.kwargs.get("post_id"))
        serializer.save(user=self.request.user, post=post)

# Comment Retrieve, Update, Destroy View
class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Ensure only comments related to the requested post are accessed."""
        return Comment.objects.filter(post__id=self.kwargs["post_id"])

# Like Post View
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_post(request, post_id):
    try:
        post = get_object_or_404(CommunityPost, id=post_id)
        user = request.user

        if post.user == user:
            raise PermissionDenied("You cannot like/unlike your own post.")

        if user in post.likes.all():
            post.likes.remove(user)  # Unlike the post
        else:
            post.likes.add(user)  # Like the post

        return Response({"detail": "Post liked/unliked successfully."}, status=status.HTTP_200_OK)

    except CommunityPost.DoesNotExist:
        return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
