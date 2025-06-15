from rest_framework import serializers
from kanban_app.models import Board, Task, Comment
from auth_app.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user representation in the API.
    Includes full name if available, otherwise uses email.
    """
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    def get_fullname(self, obj):
        """
        Returns the user's full name if available, otherwise the email.
        """
        if getattr(obj, "full_name", None):
            return obj.full_name
        return obj.email

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for representing comments on a task.
    Shows author's full name if available; uses email or 'Unknown' otherwise.
    """
    author = serializers.SerializerMethodField()
    content = serializers.CharField(source="text")

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]

    def get_author(self, obj):
        """
        Returns author's full name if present, otherwise email or 'Unknown'.
        """
        if obj.author:
            return getattr(obj.author, "full_name", obj.author.email)
        return "Unknown"

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed task representation.
    Includes display status, comments, assignee and reviewer info.
    """
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    comments = CommentSerializer(many=True, read_only=True)
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assignee",
        write_only=True,
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="reviewer",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "status_display",
            "priority",
            "assignee",
            "assignee_id",
            "reviewer",
            "reviewer_id",
            "due_date",
            "created_by",
            "created_at",
            "comments",
        ]
        read_only_fields = [
            "id", "created_by", "created_at", "comments"
        ]

class TaskListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing tasks in a board or filter context.
    Shows basic task info plus assignee, reviewer, and comment count.
    """
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        """
        Returns the number of comments for this task.
        """
        return obj.comments.count()


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for board representation in the API.
    Includes members, tasks (summary), and owner ID.
    """
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskListSerializer(many=True, read_only=True)
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    class Meta:
        model = Board
        fields = [
            "id", "title", "owner_id", "members", "tasks", "created_at"
        ]
        read_only_fields = ["id", "owner_id", "created_at"]