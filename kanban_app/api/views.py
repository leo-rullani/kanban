from rest_framework import generics
from kanban_app.models import Board, Task, Comment  # Comment ergänzt
from .serializers import BoardSerializer, TaskSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail  # <--- Neu
from rest_framework import serializers
from auth_app.models import User

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
        return Board.objects.filter(members=user) | Board.objects.filter(owner=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().distinct()
        result = []
        for board in queryset:
            tasks = board.tasks.all()
            result.append({
                "id": board.id,
                "title": board.title,
                "member_count": board.members.count(),
                "ticket_count": tasks.count(),
                "tasks_to_do_count": tasks.filter(status='todo').count(),
                "tasks_high_prio_count": tasks.filter(status='todo', description__icontains='prio:high').count(),
                "owner_id": board.owner.id if board.owner else None,
            })
        return Response(result)

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()
        members = data.get('members', [])
        if user.id not in members:
            members.append(user.id)  # Füge den Owner immer als Member hinzu

        serializer = self.get_serializer(data={**data, "members": members})
        serializer.is_valid(raise_exception=True)
        board = serializer.save(owner=user)
        board.members.add(*members)  # Nochmals für Sicherheit (idempotent)
        board.save()

        # Für Response wie spezifiziert:
        tasks = board.tasks.all()
        resp = {
            "id": board.id,
            "title": board.title,
            "member_count": board.members.count(),
            "ticket_count": tasks.count(),
            "tasks_to_do_count": tasks.filter(status='todo').count(),
            "tasks_high_prio_count": tasks.filter(status='todo', description__icontains='prio:high').count(),
            "owner_id": board.owner.id if board.owner else None,
        }
        return Response(resp, status=status.HTTP_201_CREATED)


# Board-Detail/Update/Delete (einzelnes Board)
class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        board = self.get_object()
        user = request.user

        # Berechtigung prüfen
        if not (
            user == board.owner or
            user in board.members.all() or
            user.is_superuser or
            user.email.lower() in BBM_EMAILS
        ):
            return Response({'detail': 'Keine Berechtigung, dieses Board zu ändern.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data

        # Titel aktualisieren, falls vorhanden
        if 'title' in data:
            board.title = data['title']

        # Mitglieder aktualisieren, falls vorhanden
        if 'members' in data:
            member_ids = data['members']
            # Prüfe, ob alle IDs existieren
            valid_members = User.objects.filter(id__in=member_ids)
            if valid_members.count() != len(member_ids):
                return Response({'detail': 'Ungültige Mitglieder-IDs.'}, status=status.HTTP_400_BAD_REQUEST)
            # Mitglieder setzen (ersetzen alle bisherigen Mitglieder)
            board.members.set(valid_members)

        board.save()

        # Spezifisches Response-Format mit owner_data und members_data
        owner = board.owner
        owner_data = {
            "id": owner.id,
            "email": owner.email,
            "fullname": owner.full_name if hasattr(owner, 'full_name') else str(owner)
        }

        members_data = []
        for m in board.members.all():
            members_data.append({
                "id": m.id,
                "email": m.email,
                "fullname": m.full_name if hasattr(m, 'full_name') else str(m)
            })

        response_data = {
            "id": board.id,
            "title": board.title,
            "owner_data": owner_data,
            "members_data": members_data
        }

        return Response(response_data, status=status.HTTP_200_OK)

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

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Gibt alle Kommentare zu einem bestimmten Task (über die URL) zurück.
        """
        task_id = self.kwargs.get('task_id')
        return Comment.objects.filter(task__id=task_id)

    def perform_create(self, serializer):
        user = self.request.user
        task_id = self.kwargs.get('task_id')
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise serializers.ValidationError("Task not found.")

        # Nur Owner, Member, BBM, Superuser dürfen kommentieren
        if (
            user == task.board.owner or
            user in task.board.members.all() or
            user.is_superuser or
            user.email.lower() in BBM_EMAILS
        ):
            # Kommentar speichern
            comment = serializer.save(author=user, task=task)
            
            # --- MAIL-VERSAND AN ALLE RELEVANTEN ROLLEN ---
            recipients = set()
            if task.assignee and task.assignee.email:
                recipients.add(task.assignee.email)
            if task.reviewer and task.reviewer.email:
                recipients.add(task.reviewer.email)
            if task.board.owner and task.board.owner.email:
                recipients.add(task.board.owner.email)

            if recipients:
                send_mail(
                    subject=f"[KanMind] Neuer Kommentar zu Task: {task.title}",
                    message=(
                        f"Hi,\n\n"
                        f"Es wurde ein neuer Kommentar zu deinem Task '{task.title}' hinterlegt.\n\n"
                        f"Kommentar:\n{comment.text}\n\n"
                        f"Von: {user.email}\n"
                        f"Board: {task.board.title}\n\n"
                        f"Viele Grüße\nDein KanMind-System"
                    ),
                    from_email="leugzim.rullani@bbmproductions.ch",  # oder None für DEFAULT_FROM_EMAIL
                    recipient_list=list(recipients),
                    fail_silently=True,
                )
        else:
            raise serializers.ValidationError("Keine Berechtigung, diesen Task zu kommentieren.")

class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        user = request.user
        # Nur Author, Superuser, BBM dürfen Kommentar löschen
        if not (
            user == comment.author or
            user.is_superuser or
            user.email.lower() in BBM_EMAILS
        ):
            return Response({'detail': 'Keine Berechtigung, diesen Kommentar zu löschen.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
