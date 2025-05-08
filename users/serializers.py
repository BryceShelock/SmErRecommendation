from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'points',
            'achievements', 'favorite_genres',
            'total_bookings', 'total_reviews',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'points', 'achievements',
            'total_bookings', 'total_reviews',
            'created_at', 'updated_at'
        ] 