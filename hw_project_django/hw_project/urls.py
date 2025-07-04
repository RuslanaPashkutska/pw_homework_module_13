from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("quotes.urls")),
    path("users/", include("users.urls")),
    path('login/', LoginView.as_view(template_name="user/login.html")),  # alias directo
]


