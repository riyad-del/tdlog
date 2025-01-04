from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    main_level = models.CharField(max_length=255)
    sub_level = models.CharField(max_length=255)
    def __str__(self):
        return self.user.username
