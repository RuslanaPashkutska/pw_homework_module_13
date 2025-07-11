from django.contrib.auth import views as auth_views
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = "users"

urlpatterns = [
    path('signup/', views.signup_view, name="signup"),
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="quotes:root"), name="logout"),
    path("password-reset/",
         auth_views.PasswordResetView.as_view(template_name="users/password_reset.html"),
         name="password_reset"),
    path("password-reset/done/",
          auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
          name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>",
         auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset_confirm.html"),
         name="password_reset_confirm"),
    path("password-reset-complete/",
         auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
         name="password_reset_complete")


]