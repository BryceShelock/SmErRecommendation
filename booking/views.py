from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ScriptRoom, Booking
from .serializers import ScriptRoomSerializer, BookingSerializer

# Create your views here.

class ScriptRoomViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ScriptRoomSerializer
    queryset = ScriptRoom.objects.all()

    @action(detail=True, methods=['post'])
    def book(self, request, pk=None):
        script_room = self.get_object()
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user=request.user,
                script_room=script_room,
                total_price=script_room.price * serializer.validated_data['number_of_players']
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        booking = self.get_object()
        if booking.status != 'confirmed':
            return Response(
                {'error': 'Only confirmed bookings can be marked as completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'completed'
        booking.completion_time = request.data.get('completion_time')
        booking.save()
        
        # Update user points
        user = request.user
        user.points += 5  # Points for completing a booking
        user.total_bookings += 1
        user.save()
        
        return Response(BookingSerializer(booking).data)
