from django.contrib import admin
from .models import User, ScriptRoom, Booking, Store

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'gender', 'user_type', 'phone', 'points', 'total_bookings')
    list_filter = ('gender', 'user_type')
    search_fields = ('username', 'email', 'phone')

@admin.register(ScriptRoom)
class ScriptRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty', 'duration', 'min_players', 'max_players', 'price')
    list_filter = ('difficulty',)
    search_fields = ('name', 'description')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'script_room', 'date', 'time', 'player_count', 'total_price', 'status')
    list_filter = ('status', 'date')
    search_fields = ('user__username', 'script_room__name')

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'district', 'phone', 'rating')
    list_filter = ('district',)
    search_fields = ('name', 'address', 'phone')
