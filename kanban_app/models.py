from django.db import models
from auth_app.models import User


class Board(models.Model):
    """
    Modell für ein Kanban-Board.
    Enthält Titel, Owner, Mitglieder und Erstellungsdatum.
    """

    title = models.CharField(max_length=100)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_boards"
    )
    members = models.ManyToManyField(User, related_name="boards")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    """
    Modell für eine Kanban-Task.
    Enthält Titel, Beschreibung, Status, Priorität, Verantwortliche, Deadlines und Ersteller.
    """

    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name="tasks"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=30,
        choices=[
            ("to-do", "To Do"),
            ("in-progress", "In Progress"),
            ("review", "Review"),
            ("done", "Done"),
        ],
        default="todo",
    )
    priority = models.CharField(
        max_length=10,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium",
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks_assigned",
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks_reviewing",
    )
    due_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.board.title})"


class Comment(models.Model):
    """
    Kommentar zu einer Task.
    Enthält Bezug zur Task, Author, Text und Erstellungszeitpunkt.
    """

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="comments"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        author_name = self.author.email if self.author else "Unbekannt"
        return f"Kommentar von {author_name} zu Task '{self.task.title}'"
