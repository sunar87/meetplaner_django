# Generated by Django 4.2.20 on 2025-03-28 18:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customtelegramuser',
            name='username',
        ),
    ]
