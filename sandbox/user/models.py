from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True, help_text='Required. Email address')
    username = models.CharField(
        max_length=150,
        help_text='Not required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        blank=True
    )
    phone_number = models.CharField(max_length=13, blank=True)
    date_of_birth = models.DateField(blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
