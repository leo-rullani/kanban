from django.contrib import admin
from .models import Board, Task

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    search_fields = ('title', 'owner__email')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'board', 'status', 'assignee', 'created_at')
    search_fields = ('title', 'board__title', 'assignee__email')