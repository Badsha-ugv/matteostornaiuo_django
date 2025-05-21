from django.contrib import admin
from unfold.admin import ModelAdmin
# Register your models here.
from .models import Conversation


@admin.register(Conversation)
class ConversationAdmin(ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp')
