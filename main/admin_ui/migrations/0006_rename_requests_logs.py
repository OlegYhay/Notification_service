# Generated by Django 4.1.3 on 2022-12-03 10:15

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('admin_ui', '0005_rename_request_requests'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Requests',
            new_name='Logs',
        ),
    ]
