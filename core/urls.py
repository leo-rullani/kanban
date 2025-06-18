"""
URL configuration for kanban_hub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def redirect_to_api(request):
    return redirect('/api/boards/')  # Neu: passt zum neuen Standard-Endpunkt

urlpatterns = [
    path('', redirect_to_api),  # Root-URL leitet jetzt zu /api/boards/
    path("admin/", admin.site.urls),
    path("api/", include("auth_app.api.urls")),       # <--- jetzt: /api/registration/ usw.
    path("api/", include("kanban_app.api.urls")),     # <--- jetzt: /api/boards/, /api/tasks/ usw.
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)