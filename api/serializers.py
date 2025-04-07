from datetime import timedelta

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.utils import timezone

from users.models import CustomTelegramUser
from events.models import Event, EventParticipant


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
        fields = [
            'id',
            'title',
            'event_start',
            'event_end',
            'participants',
            'owner'
        ]
        read_only_fields = ['id', 'owner']

    def to_representation(self, instance):
        """Переопределяем представление для скрытия участников при необходимости"""
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if request and not self._is_participant_or_owner(instance, request.user):
            representation.pop('participants', None)

        representation.pop('owner', None)

        return representation

    def _is_participant_or_owner(self, instance, user):
        """Проверяет, является ли пользователь участником или владельцем мероприятия"""

        if instance.owner == user:
            return True

        return instance.participants.filter(id=user.id).exists()


class UserScheduleEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'event_start', 'event_end']
        read_only_fields = fields


class UserScheduleParticipationSerializer(serializers.ModelSerializer):
    event = UserScheduleEventSerializer()

    class Meta:
        model = EventParticipant
        fields = ['joined_at', 'is_active', 'event']
        read_only_fields = fields


class EventBusyPeriodSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'event_start', 'event_end', 'duration']

    def get_duration(self, obj):
        return (obj.event_end - obj.event_start).total_seconds() / 3600


class BusyTimesQuerySerializer(serializers.Serializer):
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)

    def validate(self, data):
        from_date = data.get('from_date', timezone.now().date())
        to_date = data.get('to_date', from_date + timedelta(days=30))

        if to_date < from_date:
            raise serializers.ValidationError("End date must be after start date")

        data['from_date'] = from_date
        data['to_date'] = to_date
        return data


class BusyTimesResponseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    busy_periods = EventBusyPeriodSerializer(many=True)
    total_busy_hours = serializers.FloatField()
    total_events = serializers.IntegerField()
