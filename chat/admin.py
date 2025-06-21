from django.contrib import admin
from unfold.admin import ModelAdmin
# Register your models here.
from .models import ChatRoom, ChatMessage


@admin.register(ChatRoom)
class ChatRoomAdmin(ModelAdmin):
    pass 


@admin.register(ChatMessage)
class ChatMessageAdmin(ModelAdmin):
    pass