from rest_framework import serializers
from kanban_app.models import Board, Task

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status',
            'assignee', 'reviewer', 'due_date', 'created_by', 'created_at'
        ]