from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from auth_app.models import User
from .serializers import UserSerializer
from django.contrib.auth import authenticate

class RegistrationView(APIView):
    """
    API view for user registration.
    Allows any user to register and returns an auth token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Registers a new user and returns their token and basic info.
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key,
                    "fullname": user.full_name,
                    "email": user.email,
                    "user_id": user.id,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    API view for user login using email and password.
    Returns auth token and user info on success.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticates user and returns token and basic info.
        """
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key,
                    "fullname": user.full_name,
                    "email": user.email,
                    "user_id": user.id,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_400_BAD_REQUEST,
        )

class EmailCheckView(APIView):
    """
    API view to check if an email exists (for authenticated users).
    Returns user data if found.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
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
        except User.DoesNotExist:
            return Response(
                {"detail": "Email not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)