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

    def __str__(self):
        return f'Message from {self.sender.first_name} to {self.receiver.last_name} at {self.timestamp}'
    
    class Meta:
        ordering = ['-timestamp']
    
    # format time as 20 minutes ago
    # @property
    # def time_since(self):
    #     now = timezone.now()
    #     diff = now - self.timestamp
    #     if diff.days > 0:
    #         return f'{diff.days} days ago'
    #     elif diff.seconds // 3600 > 0:
    #         return f'{diff.seconds // 3600} hours ago'
    #     elif diff.seconds // 60 > 0:
    #         return f'{diff.seconds // 60} minutes ago'
    #     else:
    #         return 'just now'

