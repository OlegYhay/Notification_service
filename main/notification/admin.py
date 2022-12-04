from django.contrib import admin
from .models import *


# Отображем наши модели в admin-ке

@admin.register(Mailing)
class MailingModel(admin.ModelAdmin):
    pass


@admin.register(Client)
class ClientModel(admin.ModelAdmin):
    pass


@admin.register(Message)
class MessageModel(admin.ModelAdmin):
    pass


@admin.register(MobileOperator)
class MobileOperatorModel(admin.ModelAdmin):
    pass


@admin.register(Tags)
class TagsModel(admin.ModelAdmin):
    pass
