from django.contrib import admin

from unfold.admin import ModelAdmin

from .models import  Notification


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ('user', 'created_at', 'is_read', 'message')
    list_editable = ('is_read', )
