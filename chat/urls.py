from django.urls import path
from . import views 

urlpatterns = [
   path("chat-list/", views.ChatListView.as_view(), name="chat-list"),
   path("chat-history/<int:room_id>/", views.ChatHistoryAPIView.as_view(), name="chat-history"),
]