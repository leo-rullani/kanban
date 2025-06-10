from django.db import models
from auth_app.models import User

class Board(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards')
    members = models.ManyToManyField(User, related_name='boards')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Task(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=[
        ('todo', 'To Do'),
        ('inprogress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ], default='todo')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks_assigned')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks_reviewing')
    due_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.board.title})"