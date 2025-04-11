from django.db import models

# Create your models here.
class Users(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255)

class LoginAttempt(models.Model):
    Remote_addr = models.CharField(max_length=150, unique=True)
    attempts = models.IntegerField(default=0)
    lockout_until = models.DateTimeField(null=True, blank=True)

