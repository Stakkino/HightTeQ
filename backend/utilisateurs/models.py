from django.db import models
from django.contrib.auth.models import AbstractUser


class Utilisateur(AbstractUser):
    ROLE = [
        ('admin', 'Administrateur'),
        ('client', 'Client'),
    ]
    role = models.CharField(max_length=10, choices=ROLE, default='client')
    telephone = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"