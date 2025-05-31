from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .recommender import recommend_script_rooms_by_gender
from booking.serializers import ScriptRoomSerializer

User = get_user_model()

class GenderBasedRecommendationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def recommend(self, request):
        user = request.user
        recommended_rooms = recommend_script_rooms_by_gender(user)
        serializer = ScriptRoomSerializer(recommended_rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)