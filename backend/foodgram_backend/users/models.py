from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=settings.USER_CHAR_LENGTH,
        unique=True,
        validators=[
            UnicodeUsernameValidator()
        ],
        error_messages={
            'unique': ('Пользователь с этим именем уже существует'),
        },
        verbose_name='username'
    )
    email = models.EmailField(
        unique=True,
        max_length=settings.EMAIL_CHAR_LENGTH,
        verbose_name='email'
    )
    first_name = models.CharField(
        max_length=settings.FIRST_NAME_LENGTH,
        verbose_name='First name'
    )
    last_name = models.CharField(
        max_length=settings.LAST_NAME_LENGTH,
        verbose_name='Last name'
    )
    password = models.CharField(
        max_length=settings.PASSWORD_LENGTH,
        verbose_name='Password'
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'], name='unique_username_email'
            )
        ]

    def __str__(self):
        return self.username


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Author',
        related_name='subscribers'
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Subscriber',
        related_name='subscribed_on'
    )

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
