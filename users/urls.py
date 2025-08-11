# users/urls.py
from django.urls import path
from users import views

app_name = "users"

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="user-login"),
    path("signup/", views.UserSignupView.as_view(), name="user-signup"),
    path("logout/", views.UserLogoutView.as_view(), name="user-logout"),  # API용
    path("me/", views.UserDetailView.as_view(), name="user-detail"),  # pk 제거
]
