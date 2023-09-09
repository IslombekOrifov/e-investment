from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'tin']


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    default_error_messages = {
        'bad_token': ('Token is not exist')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(token=self.token).blacklist()
        except TokenError:
            self.fail('bad_token')


class UserLegalStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('is_physic',)
