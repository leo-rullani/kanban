from rest_framework import generics
from kanban_app.models import Board, Task
from .serializers import BoardSerializer, TaskSerializer
from rest_framework.permissions import IsAuthenticated

# Board-List/Create (alle Boards, neues Board)
class BoardListCreateView(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

# Board-Detail/Update/Delete (einzelnes Board)
class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

# Task-List/Create (alle Tasks, neue Task)
class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

# Task-Detail/Update/Delete (einzelne Task)
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]