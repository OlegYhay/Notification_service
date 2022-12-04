from django.contrib import admin

# Register your models here.
from admin_ui.models import Logs


@admin.register(Logs)
class MailingModel(admin.ModelAdmin):
    pass
