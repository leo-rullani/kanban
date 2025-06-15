from rest_framework import generics
from kanban_app.models import Board, Task, Comment  # Comment ergänzt
from .serializers import (
    BoardSerializer,
    TaskSerializer,
    CommentSerializer,
    TaskListSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from rest_framework import serializers
from django.db import models
from django.contrib.auth import get_user_model

# Whitelist for internal BBM email addresses (all lowercase).
BBM_EMAILS = [
    "leugzim.rullani@bbmproductions.ch",
    "ts@bbmproductions.ch",
    "roli.baerlocher@bbmproductions.ch",
    "janick.gloor@bbmproductions.ch",
    "philipp.hostettler@bbmproductions.ch",
    "richi.baerlocher@bbmproductions.ch",
    "monika.herzog@bbmproductions.ch",
    "jerome.schwarz@bbmproductions.ch",
    "roland.stocker@bbmproductions.ch",
    "nadia.acquaroli@bbmproductions.ch",
    "marcel.poll@bbmproductions.ch",
    "marius.hasler@bbmproductions.ch",
    "juergen.beckmann@bbmproductions.ch",
]


class BoardListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating boards accessible to the user.
    """

    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns boards for which the user is owner or member.
        """
        user = self.request.user
        if user.is_superuser or user.email.lower() in BBM_EMAILS:
            return Board.objects.all()
        return (Board.objects.filter(members=user) |
                Board.objects.filter(owner=user))

    def list(self, request, *args, **kwargs):
        """
        Returns a custom board list including stats for each board.
        """
        queryset = self.get_queryset().distinct()
        result = [self._get_board_stats(board) for board in queryset]
        return Response(result)

    def create(self, request, *args, **kwargs):
        """
        Creates a new board and adds the owner as a member.
        """
        user = request.user
        data = request.data.copy()
        members = self._get_members_with_owner(data, user)
        serializer = self.get_serializer(data={**data, "members": members})
        serializer.is_valid(raise_exception=True)
        board = serializer.save(owner=user)
        board.members.add(*members)
        board.save()
        resp = self._get_board_stats(board)
        return Response(resp, status=status.HTTP_201_CREATED)

    def _get_members_with_owner(self, data, user):
        """
        Returns members list including the owner if missing.
        """
        members = data.get("members", [])
        if user.id not in members:
            members.append(user.id)
        return members

    def _get_board_stats(self, board):
        """
        Returns a dictionary with statistics for the given board.
        """
        tasks = board.tasks.all()
        return {
            "id": board.id,
            "title": board.title,
            "member_count": board.members.count(),
            "ticket_count": tasks.count(),
            "tasks_to_do_count": tasks.filter(status="todo").count(),
            "tasks_high_prio_count": tasks.filter(
                status="todo",
                description__icontains="prio:high"
            ).count(),
            "owner_id": board.owner.id if board.owner else None,
        }


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a single board.
    """
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        """
        Update board's title or members, permission required.
        """
        board = self.get_object()
        user = request.user
        if not self._has_update_permission(user, board):
            return Response(
                {"detail": "No permission to update this board."},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data
        self._update_title(board, data)
        error = self._update_members(board, data)
        if error:
            return error

        board.save()
        return Response(
            self._get_response_data(board), status=status.HTTP_200_OK
        )

    def _has_update_permission(self, user, board):
        """
        Checks if the user is allowed to update the board.
        """
        return (
            user == board.owner
            or user in board.members.all()
            or user.is_superuser
            or user.email.lower() in BBM_EMAILS
        )

    def _update_title(self, board, data):
        """
        Updates the board's title if present in request data.
        """
        if "title" in data:
            board.title = data["title"]

    def _update_members(self, board, data):
        """
        Updates the board's members if present in request data.
        Returns a Response on error, else None.
        """
        if "members" in data:
            member_ids = data["members"]
            valid_members = User.objects.filter(id__in=member_ids)
            if valid_members.count() != len(member_ids):
                return Response(
                    {"detail": "Invalid member IDs."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            board.members.set(valid_members)
        return None

    def _get_response_data(self, board):
        """
        Builds response dict with owner and members data.
        """
        owner = board.owner
        owner_data = {
            "id": owner.id,
            "email": owner.email,
            "fullname": (
                owner.full_name if hasattr(owner, "full_name") else str(owner)
            ),
        }
        members_data = [
            {
                "id": m.id,
                "email": m.email,
                "fullname": (
                    m.full_name if hasattr(m, "full_name") else str(m)
                ),
            }
            for m in board.members.all()
        ]
        return {
            "id": board.id,
            "title": board.title,
            "owner_data": owner_data,
            "members_data": members_data,
        }

    def destroy(self, request, *args, **kwargs):
        """
        Delete the board if the user has permission.
        """
        board = self.get_object()
        user = request.user
        if not (
            user == board.owner
            or user.is_superuser
            or user.email.lower() in BBM_EMAILS
        ):
            return Response(
                {"detail": "No permission to delete this board."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)



class TaskListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating tasks, with filtering.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns tasks filtered by user permissions and query params.
        """
        queryset = self._filter_by_user(Task.objects.all())
        return self._filter_by_params(queryset)

    def _filter_by_user(self, queryset):
        user = self.request.user
        if user.is_superuser or user.email.lower() in BBM_EMAILS:
            return queryset
        return queryset.filter(board__members=user)

    def _filter_by_params(self, queryset):
        params = self.request.query_params
        if params.get("status"):
            queryset = queryset.filter(status=params.get("status"))
        if params.get("board"):
            queryset = queryset.filter(board=params.get("board"))
        if params.get("assignee"):
            queryset = queryset.filter(assignee=params.get("assignee"))
        if params.get("due_date"):
            queryset = queryset.filter(due_date=params.get("due_date"))
        return queryset

    def perform_create(self, serializer):
        """
        Saves the task if the user has permission on the board.
        """
        user = self.request.user
        board = serializer.validated_data["board"]
        if self._has_board_permission(user, board):
            serializer.save(created_by=user)
        else:
            raise PermissionError(
                "No permission to create task on this board."
            )

    def _has_board_permission(self, user, board):
        """
        Checks if the user can create tasks on this board.
        """
        return (
            user == board.owner or
            user in board.members.all() or
            user.is_superuser or
            user.email.lower() in BBM_EMAILS
        )

    def create(self, request, *args, **kwargs):
        """
        Handles custom assignee/reviewer assignment and returns stats.
        """
        data = request.data.copy()
        assignee, reviewer, error = self._get_users_from_data(data)
        if error:
            return error
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            created_by=request.user,
            assignee=assignee,
            reviewer=reviewer
        )
        return Response(
            self._get_task_response(serializer.instance),
            status=status.HTTP_201_CREATED
        )

    def _get_users_from_data(self, data):
        """
        Returns assignee, reviewer objects, or error response if not found.
        """
        assignee = reviewer = None
        try:
            if data.get("assignee_id"):
                assignee = User.objects.get(id=data.pop("assignee_id"))
            if data.get("reviewer_id"):
                reviewer = User.objects.get(id=data.pop("reviewer_id"))
        except User.DoesNotExist:
            return None, None, Response(
                {"detail": "Assignee or Reviewer not found."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return assignee, reviewer, None

    def _get_task_response(self, task):
        """
        Returns a dictionary for the created task (comments_count only).
        """
        return {
            "id": task.id,
            "board": task.board.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "assignee": self._get_user_info(task.assignee),
            "reviewer": self._get_user_info(task.reviewer),
            "due_date": task.due_date,
            "comments_count": task.comments.count(),
        }

    def _get_user_info(self, user):
        """
        Returns user details or None if no user is assigned.
        """
        if not user:
            return None
        return {
            "id": user.id,
            "email": user.email,
            "fullname": getattr(user, "full_name", user.email),
        }


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a single task.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        """
        Update a task if the user has permission on the related board.
        """
        task = self.get_object()
        user = request.user
        if not self._has_permission(user, task):
            return Response(
                {"detail": "No permission to update this task."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a task if the user has permission on the related board.
        """
        task = self.get_object()
        user = request.user
        if not self._has_permission(user, task):
            return Response(
                {"detail": "No permission to delete this task."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    def _has_permission(self, user, task):
        """
        Checks if the user has permission to modify or delete the task.
        """
        return (
            user == task.board.owner
            or user in task.board.members.all()
            or user.is_superuser
            or user.email.lower() in BBM_EMAILS
        )


class CommentListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating comments on a specific task.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns all comments for a specific task (by URL).
        """
        task_id = self.kwargs.get("task_id")
        return Comment.objects.filter(task__id=task_id)

    def perform_create(self, serializer):
        """
        Creates a comment if the user has permission, sends email notification.
        """
        user = self.request.user
        task = self._get_task_or_raise()
        if not self._can_comment(user, task):
            raise serializers.ValidationError(
                "No permission to comment on this task."
            )
        comment = serializer.save(author=user, task=task)
        recipients = self._get_notification_recipients(task)
        if recipients:
            self._send_comment_mail(task, comment, user, recipients)

    def _get_task_or_raise(self):
        """
        Gets the Task by URL param or raises a ValidationError.
        """
        task_id = self.kwargs.get("task_id")
        try:
            return Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise serializers.ValidationError("Task not found.")

    def _can_comment(self, user, task):
        """
        Checks if the user can comment on the given task.
        """
        return (
            user == task.board.owner
            or user in task.board.members.all()
            or user.is_superuser
            or user.email.lower() in BBM_EMAILS
        )

    def _get_notification_recipients(self, task):
        """
        Returns a set of email addresses to notify about the comment.
        """
        recipients = set()
        for u in [task.assignee, task.reviewer, task.board.owner]:
            if u and u.email:
                recipients.add(u.email)
        return recipients

    def _send_comment_mail(self, task, comment, user, recipients):
        """
        Sends a notification email to the recipients about the new comment.
        """
        send_mail(
            subject=f"[KanMind] New comment on task: {task.title}",
            message=(
                f"Hi,\n\n"
                f"A new comment was added to your task '{task.title}'.\n\n"
                f"Comment:\n{comment.text}\n\n"
                f"By: {user.email}\n"
                f"Board: {task.board.title}\n\n"
                f"Best regards\nYour KanMind system"
            ),
            from_email="leugzim.rullani@bbmproductions.ch",
            recipient_list=list(recipients),
            fail_silently=True,
        )

import logging
from django.http import Http404

logger = logging.getLogger(__name__)

class CommentDeleteView(generics.DestroyAPIView):
    """
    API view for deleting a specific comment on a task.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Returns the comment object for the given task and comment ID.
        Raises 404 if not found.
        """
        task_id = self.kwargs.get("task_id")
        comment_id = self.kwargs.get("pk")
        logger.debug(
            f"Delete comment request: task_id={task_id}, comment_id={comment_id}"
        )
        try:
            return Comment.objects.get(id=comment_id, task__id=task_id)
        except Comment.DoesNotExist:
            logger.debug(
                f"Comment with id={comment_id} and task_id={task_id} not found"
            )
            raise Http404("Comment or Task not found.")

    def destroy(self, request, *args, **kwargs):
        """
        Deletes a comment if the user has permission.
        """
        comment = self.get_object()
        user = request.user
        if not self._has_permission(user, comment):
            return Response(
                {"detail": "No permission to delete this comment."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    def _has_permission(self, user, comment):
        """
        Checks if the user can delete the comment.
        """
        return (
            user == comment.author
            or user.is_superuser
            or user.email.lower() in BBM_EMAILS
        )

class AssignedToMeTaskListView(generics.ListAPIView):
    """
    API view that lists all tasks assigned to or to be reviewed by the user.
    """
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns tasks where the user is assignee or reviewer.
        """
        user = self.request.user
        return Task.objects.filter(
            models.Q(assignee=user) | models.Q(reviewer=user)
        ).distinct()

class ReviewingTaskListView(generics.ListAPIView):
    """
    API view that lists all tasks the user is assigned to review.
    """
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns tasks where the user is reviewer.
        """
        user = self.request.user
        return Task.objects.filter(reviewer=user)


User = get_user_model()


class EmailCheckView(generics.GenericAPIView):
    """
    API view to check if an email exists in the user database.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Returns user data if the email exists, else 404.
        """
        email = request.query_params.get("email")
        if not email:
            return Response(
                {"detail": "Email query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(email=email)
            data = {
                "id": user.id,
                "email": user.email,
                "fullname": getattr(user, "full_name", user.email),
            }
            return Response(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"detail": "Email not found."},
                status=status.HTTP_404_NOT_FOUND,
            )