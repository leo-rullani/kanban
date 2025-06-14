from django.urls import path
from .views import (
    BoardListCreateView, BoardDetailView,
    TaskListCreateView, TaskDetailView,
    CommentListCreateView, CommentDeleteView,
    AssignedToMeTaskListView, ReviewingTaskListView,
    EmailCheckView  # <--- importiere deine EmailCheckView
)

urlpatterns = [
    # Boards
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    
    # Tasks
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/assigned-to-me/', AssignedToMeTaskListView.as_view(), name='tasks-assigned-to-me'),
    path('tasks/reviewing/', ReviewingTaskListView.as_view(), name='tasks-reviewing'),

    # Kommentare
    path('tasks/<int:task_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),

    # Email check endpoint ergänzen
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]