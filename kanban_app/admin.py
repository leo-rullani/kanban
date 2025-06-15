from django.contrib import admin
from .models import Board, Task

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Board model.
    Displays title, owner, and creation date in the admin list.
    Allows searching by board title and owner's email.
    """
    list_display = ("title", "owner", "created_at")
    search_fields = ("title", "owner__email")

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Task model.
    Displays title, board, status, assignee, and creation date in the admin list.
    Allows searching by task title, board title, and assignee's email.
    """
    list_display = ("title", "board", "status", "assignee", "created_at")
    search_fields = ("title", "board__title", "assignee__email")