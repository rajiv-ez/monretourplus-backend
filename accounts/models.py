from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    
    def __str__(self):
        admin = '(admin)' if self.is_admin  else ""
        return f"{self.username} {admin}"
    