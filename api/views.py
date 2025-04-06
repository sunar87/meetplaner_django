from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

from users.models import CustomTelegramUser
from events.models import Event, EventParticipant
from .serializers import (
    CustomUserCreateSerializer,
    CustomUserSerializer,
    EmailTokenObtainPairSerializer,
    EventSerializer
)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomTelegramUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['post'], url_path='register')
    def create_user(self, request):
        serializer = CustomUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': CustomUserSerializer(user).data,
            'message': 'Пользователь успешно зарегистрирован'
        },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['POST'], url_path='login')
    def login(self, request):
        serializer = EmailTokenObtainPairSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.validated_data)


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.prefetch_related('participants')
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def _get_participation(self, event, user):
        """Вспомогательный метод для получения участия"""
        return EventParticipant.objects.filter(
            event=event,
            participant=user
        ).first()

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    @action(detail=True, methods=['POST'])
    def join(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        user = request.user

        if self._get_participation(event, user):
            return Response(
                {"error": "Вы уже участвуете в этом мероприятии."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if event.event_end < timezone.now():
            return Response(
                {"error": "Мероприятие уже завершилось."},
                status=status.HTTP_400_BAD_REQUEST
            )

        EventParticipant.objects.create(
            event=event,
            participant=user,
            is_active=True
        )

        serializer = self.get_serializer(event)
        return Response(
            {
                "message": "Вы успешно присоединились к мероприятию.",
                "event": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['POST'])
    def reject(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        user = request.user

        participation = self._get_participation(event, user)

        if not participation:
            return Response(
                {"error": "Вы не участвовали в этом мероприятии."},
                status=status.HTTP_400_BAD_REQUEST
            )

        participation.delete()

        serializer = self.get_serializer(event)
        return Response(
            {
                "message": "Вы больше не участвуете в мероприятии.",
                "event": serializer.data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['GET'])
    def my_events(self, request):
        """Список мероприятий текущего пользователя"""
        user_events = Event.objects.filter(
            participants=request.user
        ).order_by('event_start')
        serializer = self.get_serializer(user_events, many=True)
        return Response(serializer.data)
