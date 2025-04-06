from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

from users.models import CustomTelegramUser
from events.models import Event


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomTelegramUser
        fields = (
            'id',
            'email',
            'timezone',
            'telegram_id',
            'notifications_enabled',
            'last_login',
            'date_joined'
        )
        read_only_fields = ('last_login', 'date_joined')


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomTelegramUser
        fields = (
            'email',
            'password',
            'timezone',
            'telegram_id',
            'notifications_enabled'
        )

    def create(self, validated_data):
        user = CustomTelegramUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            timezone='UTC',
            notifications_enabled=False,
            telegram_id=None
        )
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        authenticate_kwargs = {
            'email': attrs['email'],
            'password': attrs['password']
        }

        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        if self.user is None:
            raise serializers.ValidationError("Неверный email или пароль")

        if not self.user.is_active:
            raise serializers.ValidationError("Аккаунт неактивен")

        data = {}
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = {
            'email': self.user.email,
            'timezone': self.user.timezone,
            'telegram_id': self.user.telegram_id,
            'notifications_enabled': self.user.notifications_enabled
        }

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['timezone'] = user.timezone
        return token


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomTelegramUser
        fields = ['id', 'email']


class EventSerializer(serializers.ModelSerializer):
    event_start = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    event_end = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    participants = ParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        read_only_fields = ('owner',)
        fields = [
            'id',
            'title',
            'event_start',
            'event_end',
            'participants'
        ]
        read_only_fields = ['id']
