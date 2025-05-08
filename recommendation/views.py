from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta
from .models import UserPreference, UserInteraction, Recommendation
from .services import RecommendationService
from .serializers import (
    UserPreferenceSerializer,
    UserInteractionSerializer,
    RecommendationSerializer
)

# Create your views here.

class UserPreferenceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPreferenceSerializer

    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserInteractionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserInteractionSerializer

    def get_queryset(self):
        return UserInteraction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RecommendationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RecommendationSerializer
    recommendation_service = RecommendationService()

    def get_queryset(self):
        return Recommendation.objects.filter(
            user=self.request.user,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-score')

    @action(detail=False, methods=['post'])
    def generate(self, request):
        recommendations = self.recommendation_service.get_recommendations(
            user=request.user,
            limit=10
        )
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        recommendation = self.get_object()
        recommendation.is_viewed = True
        recommendation.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def top_script_rooms(self, request):
        recent_date = timezone.now() - timedelta(days=30)
        
        top_rooms = ScriptRoom.objects.annotate(
            recent_bookings=Count('booking', filter=models.Q(
                booking__created_at__gte=recent_date
            )),
            recent_reviews=Count('review', filter=models.Q(
                review__created_at__gte=recent_date
            )),
            avg_rating=Avg('review__rating')
        ).order_by('-recent_bookings', '-avg_rating')[:10]
        
        serializer = ScriptRoomSerializer(top_rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def user_achievements(self, request):
        user = request.user
        achievements = {
            'total_bookings': user.total_bookings,
            'total_reviews': user.total_reviews,
            'points': user.points,
            'achievements': user.achievements
        }
        return Response(achievements)
