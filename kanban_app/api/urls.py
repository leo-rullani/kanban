from django.urls import path
from .views import (
    BoardListCreateView, BoardDetailView,
    TaskListCreateView, TaskDetailView,
    CommentListCreateView, CommentDeleteView,    # <--- HINZUGEFÜGT!
    AssignedToMeTaskListView, ReviewingTaskListView                     # <--- NEU importiert!
)

urlpatterns = [
    # Boards
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    
    # Tasks
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/assigned-to-me/', AssignedToMeTaskListView.as_view(), name='tasks-assigned-to-me'),  # <--- NEU

    # Kommentare
    # Alle Kommentare zu einem Task auflisten & neuen Kommentar anlegen
    path('tasks/<int:task_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    # Einzelnen Kommentar löschen
    path('comments/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
    path('tasks/reviewing/', ReviewingTaskListView.as_view(), name='tasks-reviewing'),

]