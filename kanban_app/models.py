from django.db import models
from auth_app.models import User
class Board(models.Model):
    """
    Model representing a Kanban board.
    Fields:
        - title: The name of the board.
        - owner: The user who owns the board.
        - members: Users who are members of the board.
        - created_at: The date and time the board was created.
    """

    title = models.CharField(
        max_length=100,
        help_text="The title of the board (max. 100 characters)."
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_boards",
        help_text="The user who owns this board."
    )
    members = models.ManyToManyField(
        User,
        related_name="boards",
        help_text="Users who are members of this board."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the board was created."
    )

    def __str__(self):
        """
        Return the board's title as its string representation.
        """
        return self.title

class Task(models.Model):
    """
    Model representing a Kanban task.
    Fields:
        - board: The board to which this task belongs.
        - title: Title of the task.
        - description: Detailed description of the task.
        - status: Current workflow status of the task.
        - priority: Task priority (low, medium, high).
        - assignee: User responsible for the task.
        - reviewer: User who reviews the task.
        - due_date: Deadline for task completion.
        - created_by: User who created the task.
        - created_at: Date and time when the task was created.
    """

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="tasks",
        help_text="Reference to the board this task belongs to."
    )
    title = models.CharField(
        max_length=255,
        help_text="Title of the task (max. 255 characters)."
    )
    description = models.TextField(
        blank=True,
        help_text="Optional: Description of the task."
    )
    status = models.CharField(
        max_length=30,
        choices=[
            ("to-do", "To Do"),
            ("in-progress", "In Progress"),
            ("review", "Review"),
            ("done", "Done"),
        ],
        default="to-do",  # Corrected default value
        help_text="Current status in the workflow."
    )
    priority = models.CharField(
        max_length=10,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium",
        help_text="Priority level of the task."
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks_assigned",
        help_text="User assigned to complete this task."
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks_reviewing",
        help_text="User assigned to review this task."
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Optional: Due date for this task."
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks",
        help_text="User who created this task."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the task was created."
    )

    def __str__(self):
        """
        Return a string showing the task title and its board for display purposes.
        """
        return f"{self.title} ({self.board.title})"


class Comment(models.Model):
    """
    Model representing a comment on a task.
    Fields:
        - task: The task to which this comment belongs.
        - author: The user who wrote the comment.
        - text: The content of the comment.
        - created_at: Date and time when the comment was created.
    """

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="Task to which this comment belongs."
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="comments",
        help_text="User who wrote the comment."
    )
    text = models.TextField(
        help_text="Content of the comment."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the comment was created."
    )

    def __str__(self):
        """
        Return a string showing the author and the task title.
        If the author is deleted, 'Unknown' is shown as author.
        """
        author_name = self.author.email if self.author else "Unknown"
        return f"Comment by {author_name} on task '{self.task.title}'"