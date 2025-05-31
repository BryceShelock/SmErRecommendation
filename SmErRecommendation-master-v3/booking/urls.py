from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views

router = DefaultRouter()
router.register(r'rooms', views.ScriptRoomViewSet, basename='room')
router.register(r'bookings', views.BookingViewSet, basename='booking')
router.register(r'stores', views.StoreViewSet, basename='store')

app_name = 'booking'

urlpatterns = [
    path('', views.index, name='index'),
    
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('stores/', views.store_list, name='store_list'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('api/', include(router.urls)),
    
    path('fetch_community_posts', views.fetch_community_posts, name='fetch_community_posts'),
    path('store_recommendation', views.store_recommendation, name='store_recommendation'),
    path('script_room_recommendation', views.script_room_recommendation, name='script_room_recommendation'),
]