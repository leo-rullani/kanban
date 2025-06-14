from rest_framework import serializers
from kanban_app.models import Board, Task, Comment
from auth_app.models import User  # <-- User kommt aus auth_app!

class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        # Holt full_name oder Fallback auf E-Mail
        if getattr(obj, "full_name", None):
            return obj.full_name
        return obj.email  # Fallback: gibt immer etwas zurück

class CommentSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='author.email', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'author_email', 'text', 'created_at']
        read_only_fields = ['id', 'task', 'author', 'author_email', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'status_display',
            'assignee', 'reviewer', 'due_date', 'created_by', 'created_at',
            'comments'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'comments']

class BoardSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks', 'created_at']
        read_only_fields = ['id', 'owner_id', 'created_at']