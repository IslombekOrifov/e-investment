from rest_framework import generics, status, permissions
from rest_framework.response import Response

from django.utils.timezone import now
from datetime import timedelta, datetime


from uuid import uuid4

# It'll be used in cellery
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
import six

from .serializers import (
    UserLegalStatusSerializer, UserProfileSerializer, UserInfoUpdateSerializer,
    UserPasswordUpdateSerializer, ResetUserPasswordSerializer
)


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )


account_activation_token = TokenGenerator()


from .models import User, EmailActivation
from .serializers import RegisterSerializer, LogoutSerializer
from data.models import MainData, InformativeData, FinancialData, AllData, Currency


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(user.password)
            user.is_active = False
            if user.tin != '':
                user.is_physic = False
            user.save()

            main_data = MainData.objects.create(
                user=user,
            )
            informative_data = InformativeData.objects.create(
                user=user,
            )
            financial_data = FinancialData.objects.create(
                user=user, currency=Currency.objects.first()
            )
            AllData.objects.create(
                main_data=main_data,
                informative_data=informative_data,
                financial_data=financial_data,
                user=user
            )

            # It'll be used in cellery START
            domain = get_current_site(self.request).domain
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = account_activation_token.make_token(user)
            resend_url_token = account_activation_token.make_token(user)

            EmailActivation.objects.create(
                user=user,
                email=user.email,
                token=token,
                resend_url_token=resend_url_token
            )

            mail_subject = 'Verify your email address'
            message = f'Click here for confirm your registration.\nhttp://{domain}/accounts/email-activation/{uid}/{token}'
            user.email_user(mail_subject, message)
            # It'll be used in cellery END

            return Response('User created successfully')
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class EmailActivationView(generics.RetrieveAPIView):
    serializer_class = None

    def get_serializer_class(self):
        return ''

    def retrieve(self, request, *args, **kwargs):
        uid = force_str(urlsafe_base64_decode(kwargs['uid']))
        token = kwargs['token']
        try:
            email_activation = EmailActivation.objects.get(user=uid)
            if email_activation.token == token:
                if email_activation.date >= now() - timedelta(days=2):
                    email_activation.user.email = email_activation.email
                    email_activation.user.is_active = True
                    email_activation.user.save(force_update=True)
                    email_activation.num_sent = 0
                    email_activation.save(force_update=True)
                    return Response({'Email verified successfully'}, status.HTTP_200_OK)
                else:
                    return Response({'Token expired'}, status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'Invalid token'}, status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'Bad request'}, status.HTTP_400_BAD_REQUEST)


class ResendEmailView(generics.RetrieveAPIView):
    serializer_class = None

    def get_serializer_class(self):
        return ''

    def retrieve(self, request, *args, **kwargs):
        uid = force_str(urlsafe_base64_decode(kwargs['uid']))
        token = kwargs['token']
        try:
            email_activation = EmailActivation.objects.get(user=uid)
            if email_activation.resend_url_token == token:
                domain = get_current_site(self.request).domain
                uid = urlsafe_base64_encode(force_bytes(email_activation.user.id))
                token = account_activation_token.make_token(email_activation.user)
                resend_url_token = account_activation_token.make_token(email_activation.user)
                if email_activation.num_sent < 5:
                    email_activation.token = token
                    email_activation.num_sent += 1
                    email_activation.resend_url_token = resend_url_token
                    email_activation.save(force_update=True)

                    # It'll be used in cellery START
                    mail_subject = 'Verify your email address'
                    message = f'Click here for confirm your registration.\nhttp://{domain}/accounts/email-activation/{uid}/{token}'
                    email_activation.user.email_user(mail_subject, message)
                    # It'll be used in cellery END
                else:
                    if email_activation.date <= now() - timedelta(hours=1):
                        email_activation.token = token
                        email_activation.num_sent = 1
                        email_activation.resend_url_token = resend_url_token
                        email_activation.save(force_update=True)

                        # It'll be used in cellery START
                        mail_subject = 'Verify your email address'
                        message = f'Click here for confirm your registration.\nhttp://{domain}/accounts/email-activation/{uid}/{token}'
                        email_activation.user.email_user(mail_subject, message)
                        # It'll be used in cellery END
                    else:
                        return Response({'Please! Try again little later'}, status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'Invalid token'}, status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'Bad request'}, status.HTTP_400_BAD_REQUEST)


class LogoutView(generics.CreateAPIView):
    serializer_class = LogoutSerializer
    permissions = [permissions.IsAuthenticated]


class UserLegalStatusView(generics.RetrieveAPIView):
    serializer_class = UserLegalStatusSerializer
    permissions = [permissions.IsAuthenticated]

    def get_object(self):
        return User.objects.filter(pk=self.request.user.pk).first()
    
    

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permissions = [permissions.IsAuthenticated]

    def get_object(self):
        return User.objects.filter(pk=self.request.user.pk).first()


class UserInfoUpdateView(generics.CreateAPIView):
    serializer_class = UserInfoUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = User.objects.get(id=self.request.user.id)  # Use get to retrieve a single user
        cd = serializer.validated_data
        for key, value in cd.items():
            setattr(user, key, value)  # Update user attributes
        user.save()  # Save the user object
             

class UserPasswordUpdateView(generics.CreateAPIView):
    serializer_class = UserPasswordUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = self.request.user
            new_password = serializer.validated_data['password']
            user.set_password(new_password)
            user.save()
            return Response({'detail': 'Password updated successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetUserPasswordView(generics.CreateAPIView):
    serializer_class = ResetUserPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data['email'])
            if user:
                password = serializer.validated_data['password']
                
                domain = get_current_site(self.request).domain
                uid = urlsafe_base64_encode(force_bytes(user.id))
                uid1 = urlsafe_base64_encode(force_bytes(password))
                uid2 = urlsafe_base64_encode(force_bytes(now()))
                token = account_activation_token.make_token(user)

                mail_subject = 'Password Reset'
                message = f'Click here to reset your password.\nhttp://{domain}/accounts/user-password-reset/confirm/{uid}/{uid1}/{uid2}/{token}' 
                user.email_user(mail_subject, message)
            return Response({'detail': 'We send your new password to your email.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetUserPasswordConfirmView(generics.RetrieveAPIView):
    serializer_class = None

    def get_serializer_class(self):
        return ''

    def retrieve(self, request, *args, **kwargs):
        uid = force_str(urlsafe_base64_decode(kwargs['uid']))
        uid1 = force_str(urlsafe_base64_decode(kwargs['uid1']))
        uid2 = force_str(urlsafe_base64_decode(kwargs['uid2']))
        token = kwargs['token']
        
        user = User.objects.get(pk=int(uid))
        if user:
            if account_activation_token.check_token(user, token):
                uid2_datetime = datetime.strptime(uid2, "%Y-%m-%d %H:%M:%S.%f%z")
                current_datetime = now()
                if  current_datetime - timedelta(hours=1) <= uid2_datetime <= current_datetime:
                    user.set_password(uid1) 
                    user.save()
                    return Response({'Password changed successfully'}, status.HTTP_200_OK)
                else:
                    return Response({'Token expired'}, status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'Invalid token'}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Bad request'}, status.HTTP_400_BAD_REQUEST)
