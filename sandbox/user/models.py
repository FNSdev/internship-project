from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_superuser(self, email, password, **kwargs):
        user = self.model(
            email=email,
            is_staff=True,
            is_superuser=True,
            **kwargs
        )
        user.set_password(password)
        user.save()
        return user


class User(AbstractUser):
    objects = UserManager()

    email = models.EmailField(unique=True, help_text='Required. Email address')
    username = models.CharField(
        max_length=150,
        help_text='Not required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        blank=True
    )
    phone_number = models.CharField(max_length=13, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
