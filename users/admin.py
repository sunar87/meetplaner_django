# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomTelegramUser


class CustomTelegramUserAdmin(UserAdmin):
    list_display = ('email', 'telegram_id', 'timezone', 'notifications_enabled', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'notifications_enabled')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('telegram_id', 'timezone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Notifications', {'fields': ('notifications_enabled',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'timezone'),
        }),
    )

    search_fields = ('email', 'telegram_id')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(CustomTelegramUser, CustomTelegramUserAdmin)