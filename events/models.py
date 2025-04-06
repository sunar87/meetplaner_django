from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from users.models import CustomTelegramUser


class Event(models.Model):
    owner = models.ForeignKey(CustomTelegramUser,
                              on_delete=models.CASCADE,
                              related_name='event_onwer')
    title = models.CharField(
        _('title'),
        max_length=255,
        help_text=_('Enter the event title')
    )
    event_start = models.DateTimeField(
        _('start time'),
        help_text=_('Event start date and time')
    )
    event_end = models.DateTimeField(
        _('end time'),
        help_text=_('Event end date and time')
    )
    participants = models.ManyToManyField(
        CustomTelegramUser,
        through='EventParticipant',
        related_name='events',
        verbose_name=_('participants'),
        help_text=_('Users participating in the event')
    )

    class Meta:
        ordering = ['event_start']
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        indexes = [
            models.Index(fields=['event_start']),
            models.Index(fields=['event_end']),
        ]

    def __str__(self):
        return f"{self.title} ({self.event_start:%Y-%m-%d %H:%M})"

    def clean(self):
        """Валидация временных промежутков"""
        if self.event_end <= self.event_start:
            raise ValidationError(_('End time must be after start time'))


class EventParticipant(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name=_('event'),
        related_name='event_participants'
    )
    participant = models.ForeignKey(
        CustomTelegramUser,
        on_delete=models.CASCADE,
        verbose_name=_('participant'),
        related_name='event_participations'
    )
    joined_at = models.DateTimeField(
        _('joined at'),
        auto_now_add=True
    )
    is_active = models.BooleanField(
        _('active participation'),
        default=True,
        help_text=_('Designates whether the participant is still active in the event')
    )

    class Meta:
        unique_together = ('event', 'participant')
        verbose_name = _('Event Participant')
        verbose_name_plural = _('Event Participants')
        ordering = ['-joined_at']

    def __str__(self):
        return _('%(name)s in %(event)s') % {
            'name': self.participant.email,
            'event': self.event.title
        }
