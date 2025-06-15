from django.urls import path
from .views import RegistrationView, LoginView, EmailCheckView

# API endpoints for authentication (registration, login, email check).
urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("login/", LoginView.as_view(), name="login"),
    path(
        "email-check/", EmailCheckView.as_view(), name="email-check"
    ),
]