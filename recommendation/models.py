from django.db import models
from users.models import User
from booking.models import ScriptRoom

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    genre_weights = models.JSONField(default=dict)
    difficulty_preference = models.FloatField(default=2.0)
    price_range = models.JSONField(default=dict)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"

class UserInteraction(models.Model):
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('book', 'Book'),
        ('review', 'Review'),
        ('click', 'Click'),
        ('ignore', 'Ignore')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    script_room = models.ForeignKey(ScriptRoom, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    weight = models.FloatField(default=1.0)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'script_room']),
            models.Index(fields=['interaction_type', 'timestamp'])
        ]

    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} - {self.script_room.name}"

class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    script_room = models.ForeignKey(ScriptRoom, on_delete=models.CASCADE)
    score = models.FloatField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_viewed = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-score']),
            models.Index(fields=['created_at'])
        ]

    def __str__(self):
        return f"Recommendation for {self.user.username}: {self.script_room.name} ({self.score})"
