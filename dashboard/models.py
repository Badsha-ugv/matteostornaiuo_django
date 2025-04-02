from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator


User = get_user_model()
from staff.models import Staff
from client.models import CompanyProfile, Vacancy


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)# to whom
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Notifications'   
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} - {self.message[:20]}...'

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    message = models.TextField()
    attachment = models.FileField(upload_to='reports/', blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    

    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.user} report for {self.type}'
    class Meta:
        verbose_name_plural = 'Reports'
        ordering = ['-created_at']

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

    class Meta:
        verbose_name_plural = 'FAQs'
        ordering = ['-created_at']


class TermsAndConditions(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    document = models.FileField(upload_to='terms_and_conditions/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Terms and Conditions'
        ordering = ['-created_at']