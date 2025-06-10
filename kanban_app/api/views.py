from rest_framework import generics
from kanban_app.models import Board, Task
from .serializers import BoardSerializer, TaskSerializer
from rest_framework.permissions import IsAuthenticated

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
        # Superuser oder BBM intern (Whitelist) sehen ALLE Boards
        if user.is_superuser or user.email.lower() in BBM_EMAILS:
            return Board.objects.all()
        # Freelancer sehen NUR Boards, in denen sie Member sind
        return Board.objects.filter(members=user)

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