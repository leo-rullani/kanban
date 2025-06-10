from django.urls import path
from .views import (
    BoardListCreateView, BoardDetailView,
    TaskListCreateView, TaskDetailView
)

urlpatterns = [
    # Boards
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    
    # Tasks
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
]