from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from staff.models import Staff
from client.models import CompanyProfile
from . models import ChatMessage, ChatRoom


class ChatListView(APIView):
    """
    VIEW CHAT LIST
    """
    def get(self, request):
        user = request.user
        chat_rooms = ChatRoom.objects.filter(participants=user)
        print("chat rooms:", chat_rooms)

        chat_list = []
        
        if user.is_client:
            for room in chat_rooms:
                particiapants = room.participants.exclude(id=user.id)[0]
                profile= Staff.objects.filter(user=particiapants).first()
                if profile:
                    chat_list.append({
                        "id": room.id,
                        "name": profile.user.first_name + " " + profile.user.last_name,
                        "image": profile.avatar.url if profile.avatar else None,
                        "last_message": room.messages.last().content if room.messages.exists() else "",
                        # "last_message": room.messages.last().content if room.messages.exists() else "",
                        # "timestamp": room.messages.last().timestamp if room.messages.exists() else None
                    })
        elif user.is_staff:
            for room in chat_rooms:
                particiapants = room.participants.exclude(id=user.id)[0]
                profile = CompanyProfile.objects.filter(user=particiapants).first()
                if profile:
                    chat_list.append({
                        "id": room.id,
                        "name": profile.company_name,
                        "image": profile.company_logo.url if profile.company_logo else None,
                        "last_message": room.messages.last().content if room.messages.exists() else "",
                        # "timestamp": room.messages.last().timestamp if room.messages.exists() else None
                    })
        
        
        return Response(chat_list, status=status.HTTP_200_OK)


class ChatHistoryAPIView(APIView):
    """
    VIEW CHAT HISTORY
    """
    def get(self, request, room_id):
        user = request.user
        try:
            chat_room = ChatRoom.objects.get(id=room_id, participants=user)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Chat room not found."}, status=status.HTTP_404_NOT_FOUND)

        messages = chat_room.messages.all().order_by('timestamp')
        message_list = [
            {
                "sender": message.sender.id,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "is_read": message.is_read
            } for message in messages
        ]

        return Response(message_list, status=status.HTTP_200_OK)