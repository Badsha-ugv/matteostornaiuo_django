from django.db import models

from staff.models import Staff
from client.models import CompanyProfile

from users.models import User

from django.utils import timezone

# models for chat messages

class Conversation(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    

    def __str__(self):
        return f'Message from {self.sender.first_name} to {self.receiver.last_name} at {self.timestamp}'
    
    class Meta:
        ordering = ['-timestamp']


