from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


from .views import (
    RegisterView, EmailActivationView, ResendEmailView, LogoutView, UserLegalStatusView,
    UserProfileView, UserInfoUpdateView, UserPasswordUpdateView, ResetUserPasswordView,
    ResetUserPasswordConfirmView
)


urlpatterns = [
    path('login', TokenObtainPairView.as_view()),
    path('refresh', TokenRefreshView.as_view()),
    path('logout', LogoutView.as_view()),
    path("register", RegisterView.as_view()),
    path('email-activation/<uid>/<token>', EmailActivationView.as_view()),
    path('email-resend/<uid>/<token>', ResendEmailView.as_view()),
    path("user-status", UserLegalStatusView.as_view()),
    path("user-profile-update", UserInfoUpdateView.as_view()),
    path("user-profile", UserProfileView.as_view()),
    path("user-password-update", UserPasswordUpdateView.as_view()),
    path("user-password-reset/confirm/<uid>/<uid1>/<uid2>/<token>", ResetUserPasswordConfirmView.as_view()),
    path("user-password-reset", ResetUserPasswordView.as_view()),
]
