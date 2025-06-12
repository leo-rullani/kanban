from rest_framework import serializers
from kanban_app.models import Board, Task, Comment

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='author.email', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'author_email', 'text', 'created_at']
        read_only_fields = ['id', 'task', 'author', 'author_email', 'created_at']  # <-- task auf read_only!

class TaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    # Wenn du alle Kommentare mit Task anzeigen willst (optional, kann auch weggelassen werden)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'status_display',
            'assignee', 'reviewer', 'due_date', 'created_by', 'created_at',
            'comments'  # <- Kommentare als Liste (read-only)
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'comments']