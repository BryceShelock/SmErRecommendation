from django.db import models
from users.models import User
from booking.models import ScriptRoom
from textblob import TextBlob

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    script_room = models.ForeignKey(ScriptRoom, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    sentiment_score = models.FloatField(default=0.0)
    word_count = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calculate sentiment score using TextBlob
        blob = TextBlob(self.comment)
        self.sentiment_score = blob.sentiment.polarity
        
        # Calculate word count
        self.word_count = len(self.comment.split())
        
        # Update script room rating
        super().save(*args, **kwargs)
        self.update_script_room_rating()

    def update_script_room_rating(self):
        script_room = self.script_room
        reviews = Review.objects.filter(script_room=script_room)
        if reviews.exists():
            script_room.rating = sum(review.rating for review in reviews) / reviews.count()
            script_room.total_reviews = reviews.count()
            script_room.save()

    def __str__(self):
        return f"{self.user.username} - {self.script_room.name} - {self.rating}"
