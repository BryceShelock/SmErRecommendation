from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Review
from .serializers import ReviewSerializer
from booking.models import ScriptRoom

# Create your views here.

class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user)
        
        # Update user points and achievements
        user = self.request.user
        user.points += 10  # Points for writing a review
        user.total_reviews += 1
        
        # Check for review quality achievement
        if review.word_count > 100 and review.sentiment_score > 0.5:
            if 'quality_reviewer' not in user.achievements:
                user.achievements['quality_reviewer'] = True
                user.points += 20  # Bonus points for quality review
        
        user.save()

    @action(detail=False, methods=['get'])
    def room_reviews(self, request):
        room_id = request.query_params.get('room_id')
        if not room_id:
            return Response(
                {'error': 'room_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            room = ScriptRoom.objects.get(id=room_id)
            reviews = Review.objects.filter(script_room=room)
            serializer = self.get_serializer(reviews, many=True)
            return Response(serializer.data)
        except ScriptRoom.DoesNotExist:
            return Response(
                {'error': 'Room not found'},
                status=status.HTTP_404_NOT_FOUND
            )
