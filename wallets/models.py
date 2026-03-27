from django.db import models
from django.conf import settings

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    address = models.CharField(max_length=42, unique=True)
    private_key = models.CharField(max_length=255 , null = True) 

    def __str__(self):
        return f"{self.user.username} - {self.address}"