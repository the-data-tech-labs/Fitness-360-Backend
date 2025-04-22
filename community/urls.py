# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.CommunityPostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', views.CommunityPostRetrieveUpdateDestroyView.as_view(), name='post-retrieve-update-destroy'),
    path('posts/<int:post_id>/comments/', views.CommentCreateView.as_view(), name='comment-create'),
    path('comments/<int:pk>/', views.CommentRetrieveUpdateDestroyView.as_view(), name='comment-retrieve-update-destroy'),
    path('posts/<int:post_id>/like/', views.like_post, name='like-post'),  # Add like endpoint
]