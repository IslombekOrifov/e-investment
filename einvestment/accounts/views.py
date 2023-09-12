from rest_framework import generics, status, permissions
from rest_framework.response import Response

from django.utils.timezone import now
from datetime import timedelta

# It'll be used in cellery
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
import six

from .serializers import UserLegalStatusSerializer


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )


account_activation_token = TokenGenerator()


from .models import User, EmailActivation
from .serializers import RegisterSerializer, LogoutSerializer
from data.models import MainData, InformativeData, FinancialData, AllData


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
                user=user,
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
    

class UserInfoView(generics.RetrieveAPIView):
    serializer_class = UserLegalStatusSerializer
    permissions = [permissions.IsAuthenticated]

    def get_object(self):
        return User.objects.filter(pk=self.request.user.pk).first()
