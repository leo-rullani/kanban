from rest_framework import serializers
from kanban_app.models import Board, Task, Comment
from auth_app.models import User

class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        if getattr(obj, "full_name", None):
            return obj.full_name
        return obj.email

class CommentSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='author.email', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'author_email', 'text', 'created_at']
        read_only_fields = ['id', 'task', 'author', 'author_email', 'created_at']

# Für Detail-Ansicht einzelner Tasks inkl. Kommentare
class TaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', write_only=True, required=False, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='reviewer', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'status_display',
            'priority', 'assignee', 'assignee_id', 'reviewer', 'reviewer_id',
            'due_date', 'created_by', 'created_at', 'comments'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'comments']

# Für Task-Listen-APIs (assigned-to-me, reviewing, Board-Detail)
class TaskListSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count'
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()

class BoardSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    # Für Board-Detail (tasks-Array) verwende TaskListSerializer!
    tasks = TaskListSerializer(many=True, read_only=True)
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks', 'created_at']
        read_only_fields = ['id', 'owner_id', 'created_at']