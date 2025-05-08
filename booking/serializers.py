from rest_framework import serializers
from .models import ScriptRoom, Booking

class ScriptRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScriptRoom
        fields = [
            'id', 'name', 'description', 'genre',
            'difficulty', 'duration', 'min_players',
            'max_players', 'price', 'rating',
            'total_bookings', 'total_reviews'
        ]

class BookingSerializer(serializers.ModelSerializer):
    script_room = ScriptRoomSerializer(read_only=True)
    script_room_id = serializers.PrimaryKeyRelatedField(
        queryset=ScriptRoom.objects.all(),
        write_only=True,
        source='script_room'
    )

    class Meta:
        model = Booking
        fields = [
            'id', 'script_room', 'script_room_id',
            'booking_date', 'start_time', 'end_time',
            'number_of_players', 'total_price',
            'status', 'completion_time',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'total_price', 'status',
            'created_at', 'updated_at'
        ] 