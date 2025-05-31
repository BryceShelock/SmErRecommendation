from django.contrib.auth.models import AbstractUser
from django.db import models

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

class User(AbstractUser):
    points = models.IntegerField(default=0)
    achievements = models.JSONField(default=dict)
    favorite_genres = models.JSONField(default=list)
    total_bookings = models.IntegerField(default=0)
    total_reviews = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.username