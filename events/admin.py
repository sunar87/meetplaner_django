from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Event, EventParticipant


class EventParticipantInline(admin.TabularInline):
    model = EventParticipant
    extra = 1  # Показывать 1 дополнительную пустую форму
    autocomplete_fields = ['participant']  # Включите если есть search_fields в CustomTelegramUserAdmin
    readonly_fields = ('joined_at',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_start', 'event_end', 'participants_count')
    list_filter = ('event_start', 'event_end')
    search_fields = ('title',)
    date_hierarchy = 'event_start'
    inlines = (EventParticipantInline,)

    # Убрали participants из fieldsets, так как используем промежуточную модель
    fieldsets = (
        (None, {
            'fields': ('title', ('event_start', 'event_end'))
        }),
        # Убрали раздел Participants, так как управление через inline
    )

    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = _('Participants')


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ('event', 'participant', 'joined_at', 'is_active')
    list_select_related = ('event', 'participant')
    list_filter = ('is_active', 'event')
    search_fields = ('participant__email', 'event__title')
    raw_id_fields = ('event', 'participant')
    readonly_fields = ('joined_at',)
