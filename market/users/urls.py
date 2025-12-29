from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.urls import reverse_lazy
from .views import register_view, profile_view


app_name = 'auth'

urlpatterns = [
    path("register/", register_view, name="register"),
    path("profile/", profile_view, name="profile"),
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('password-change/', PasswordChangeView.as_view(template_name='users/password_change.html', success_url=reverse_lazy('auth:password_change_done')), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),
]