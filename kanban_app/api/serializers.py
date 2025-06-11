from rest_framework import serializers
from kanban_app.models import Board, Task

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']  # <-- DAS IST NEU

class TaskSerializer(serializers.ModelSerializer):
    # Fügt ein Read-only-Feld für die Choice-Anzeige hinzu (optional)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'status_display',
            'assignee', 'reviewer', 'due_date', 'created_by', 'created_at'
        ]