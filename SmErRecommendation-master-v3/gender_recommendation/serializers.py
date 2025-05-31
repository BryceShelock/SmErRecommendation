from rest_framework import serializers
from booking.models import ScriptRoom

class ScriptRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScriptRoom
        fields = '__all__'