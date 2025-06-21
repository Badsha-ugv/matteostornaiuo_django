from django.db import models

from staff.models import Staff
from client.models import CompanyProfile

from users.models import User

from django.utils import timezone

# models for chat messages

class ChatRoomManager(models.Manager):
    def get_or_create_by_users(self, user1_id, user2_id):
        users = sorted([user1_id, user2_id])
        rooms = self.filter(participants__id=users[0]).filter(participants__id=users[1])
        for room in rooms:
            if room.participants.count() == 2:
                return room, False

        room = self.create()
        room.participants.add(*users)
        return room, True
    
class ChatRoom(models.Model):
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ChatRoomManager() 

    def __str__(self):
        return f'Chat Room {self.id} with {self.participants.count()} participants'
    
class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


    def __str__(self):
        return f'Message from {self.sender.first_name} at {self.timestamp}'
    
    class Meta:
        ordering = ['-timestamp']


# class ChatList(models.Model):
#     me = models.ForeignKey(User, on_delete=models.CASCADE)
#     to = models.ForeignKey(User, on_delete=models.CASCADE)
#     conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)

