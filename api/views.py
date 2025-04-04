from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import CustomTelegramUser
from events.models import Event
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

    @action(detail=False, methods=['post'], url_path='login')
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
