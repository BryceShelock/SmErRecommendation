from rest_framework import serializers
from .models import Review
from booking.models import ScriptRoom

class ReviewSerializer(serializers.ModelSerializer):
    script_room = serializers.PrimaryKeyRelatedField(
        queryset=ScriptRoom.objects.all()
    )

    class Meta:
        model = Review
        fields = [
            'id', 'script_room', 'rating', 'comment',
            'sentiment_score', 'word_count', 'is_verified',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'sentiment_score', 'word_count', 'is_verified',
            'created_at', 'updated_at'
        ] 