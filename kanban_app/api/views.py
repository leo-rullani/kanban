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
        if not (
            user == board.owner or
            user.is_superuser or
            user.email.lower() in BBM_EMAILS
        ):
            return Response({'detail': 'Keine Berechtigung, dieses Board zu löschen.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

# Task-List/Create (alle Tasks, neue Task) MIT FILTER!
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.all()

        # Rechte-Logik: Nur zugelassene Tasks sehen!
        if not (user.is_superuser or user.email.lower() in BBM_EMAILS):
            queryset = queryset.filter(
                board__members=user
            )

        # Filter nach Query-Parametern (optional und kombinierbar)
        status_param = self.request.query_params.get('status')
        board_param = self.request.query_params.get('board')
        assignee_param = self.request.query_params.get('assignee')
        due_date_param = self.request.query_params.get('due_date')

        if status_param:
            queryset = queryset.filter(status=status_param)
        if board_param:
            queryset = queryset.filter(board=board_param)
        if assignee_param:
            queryset = queryset.filter(assignee=assignee_param)
        if due_date_param:
            queryset = queryset.filter(due_date=due_date_param)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        board = serializer.validated_data['board']
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
        if not (
            user == task.board.owner or
            user in task.board.members.all() or
            user.is_superuser or
            user.email.lower() in BBM_EMAILS
        ):
            return Response({'detail': 'Keine Berechtigung, diesen Task zu löschen.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)