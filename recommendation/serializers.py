from rest_framework import serializers
from .models import UserPreference, UserInteraction, Recommendation
from booking.models import ScriptRoom
from reviews.models import Review

class ScriptRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScriptRoom
        fields = [
            'id', 'name', 'description', 'genre', 'difficulty',
            'duration', 'min_players', 'max_players', 'price',
            'rating', 'total_bookings', 'total_reviews'
        ]

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = [
            'id', 'genre_weights', 'difficulty_preference',
            'price_range', 'last_updated'
        ]
        read_only_fields = ['last_updated']

class UserInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInteraction
        fields = [
            'id', 'script_room', 'interaction_type',
            'timestamp', 'weight'
        ]
        read_only_fields = ['timestamp']

class RecommendationSerializer(serializers.ModelSerializer):
    script_room = ScriptRoomSerializer(read_only=True)

    class Meta:
        model = Recommendation
        fields = [
            'id', 'script_room', 'score', 'reason',
            'created_at', 'is_viewed'
        ]
        read_only_fields = ['created_at', 'is_viewed'] 