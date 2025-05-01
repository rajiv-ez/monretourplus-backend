from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.username} { "(admin)" if self.is_admin  else ""}"
    