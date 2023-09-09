from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


from .views import (
    RegisterView, EmailActivationView, ResendEmailView, LogoutView, UserLegalStatusView
)


urlpatterns = [
    path('login', TokenObtainPairView.as_view()),
    path('refresh', TokenRefreshView.as_view()),
    path('logout', LogoutView.as_view()),
    path("register", RegisterView.as_view()),
    path('email-activation/<uid>/<token>', EmailActivationView.as_view()),
    path('email-resend/<uid>/<token>', ResendEmailView.as_view()),
    path("user-status", UserLegalStatusView.as_view()),
]
