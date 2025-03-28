# Generated by Django 4.2.20 on 2025-03-28 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('users', '0002_remove_customtelegramuser_username'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customtelegramuser',
            options={'ordering': ['-date_joined'], 'verbose_name': 'Telegram User', 'verbose_name_plural': 'Telegram Users'},
        ),
        migrations.AlterModelManagers(
            name='customtelegramuser',
            managers=[
            ],
        ),
        migrations.AlterField(
            model_name='customtelegramuser',
            name='email',
            field=models.EmailField(error_messages={'unique': 'A user with that email already exists.'}, max_length=254, unique=True, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='customtelegramuser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='custom_user_groups', related_query_name='custom_user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='customtelegramuser',
            name='notifications_enabled',
            field=models.BooleanField(default=False, verbose_name='notifications enabled'),
        ),
        migrations.AlterField(
            model_name='customtelegramuser',
            name='telegram_id',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='telegram ID'),
        ),
        migrations.AlterField(
            model_name='customtelegramuser',
            name='timezone',
            field=models.CharField(default='UTC', max_length=50, verbose_name='timezone'),
        ),
        migrations.AlterField(
            model_name='customtelegramuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='custom_user_permissions', related_query_name='custom_user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
