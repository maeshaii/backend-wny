# Models for OJT users will be added here in the future.

from django.db import models
from django.conf import settings

class OjtUser(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('ongoing', 'Ongoing'),
        ('sent_to_admin', 'Sent to Admin'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ojt_profile')
    ojt_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'OJT User'
        verbose_name_plural = 'OJT Users'
        db_table = 'ojt_users'

    def __str__(self):
        return f"{self.user.f_name} {self.user.l_name} - {self.ojt_status}"
