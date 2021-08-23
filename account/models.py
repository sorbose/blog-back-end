from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class BlogUser(AbstractUser):
    USERNAME_FIELD = 'username'
    birthday = models.DateField()
    REQUIRED_FIELDS = ['birthday']

    def __str__(self):
        return self.username
