from rest_framework import generics
from kanban_app.models import Board, Task
from .serializers import BoardSerializer, TaskSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Whitelist für BBM interne E-Mail-Adressen (alle lower-case!)
BBM_EMAILS = [
    "leugzim.rullani@bbmproductions.ch",
    "ts@bbmproductions.ch",
    "roli.baerlocher@bbmproductions.ch",
    "janick.gloor@bbmproductions.ch",
    "philipp.hostettler@bbmproductions.ch",
    "richi.baerlocher@bbmproductions.ch",
    "monika.herzog@bbmproductions.ch",
    "jerome.schwarz@bbmproductions.ch",
    "roland.stocker@bbmproductions.ch",
    "nadia.acquaroli@bbmproductions.ch",
    "marcel.poll@bbmproductions.ch",
    "marius.hasler@bbmproductions.ch",
    "juergen.beckmann@bbmproductions.ch",
]

# Board-List/Create (alle Boards, neues Board)
class BoardListCreateView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.email.lower() in BBM_EMAILS:
            return Board.objects.all()
        return Board.objects.filter(members=user)

    def perform_create(self, serializer):
        user = self.request.user
        # Nur BBM/Superuser dürfen Boards anlegen!
        if user.is_superuser or user.email.lower() in BBM_EMAILS:
            serializer.save(owner=user)
        else:
            raise PermissionError("Nur BBM/Superuser dürfen Boards erstellen.")

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except PermissionError as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)

# Board-Detail/Update/Delete (einzelnes Board)
class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        board = self.get_object()
        user = request.user
        # Nur Owner/Superuser/BBM dürfen löschen
        if not (
            user == board.owner or
            user.is_superuser or
            user.email.lower() in BBM_EMAILS
        ):
            return Response({'detail': 'Keine Berechtigung, dieses Board zu löschen.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

# Task-List/Create (alle Tasks, neue Task)
class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        board = serializer.validated_data['board']
        # Nur Owner/Member/Superuser/BBM dürfen Tasks erstellen
        if (
            user == board.owner or
            user in board.members.all() or
            user.is_superuser or
            user.email.lower() in BBM_EMAILS
        ):
            serializer.save(created_by=user)
        else:
            raise PermissionError("Keine Berechtigung, Task auf diesem Board zu erstellen.")

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except PermissionError as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)

# Task-Detail/Update/Delete (einzelne Task)
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        user = request.user
        if not (
            user == task.board.owner or
            user in task.board.members.all() or
            user.is_superuser or
            user.email.lower() in BBM_EMAILS
        ):
            return Response({'detail': 'Keine Berechtigung, diesen Task zu ändern.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        user = request.user
        # Nur Owner/Member/Superuser/BBM dürfen Task löschen
        if not (
            user == task.board.owner or
            user in task.board.members.all() or
            user.is_superuser or
            user.email.lower() in BBM_EMAILS
        ):
            return Response({'detail': 'Keine Berechtigung, diesen Task zu löschen.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)