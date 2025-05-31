"""
URL configuration for script_murder_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from booking.views import (
    login_view, register_view, logout_view, my_reviews, profile,
    post_create, store_create, store_list, script_room_create, booking_create, store_detail,
    script_detail, review_create, toggle_favourite, my_favourites, post_detail
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/booking/', include('booking.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/recommendation/', include('recommendation.urls')),
    
    # Template URLs
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('index', TemplateView.as_view(template_name='index.html'), name='index'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('stores/', store_list, name='stores'),
    path('community/', TemplateView.as_view(template_name='community.html'), name='community'),
    path('profile/', profile, name='profile'),
    path('my-bookings/', TemplateView.as_view(template_name='booking/my_bookings.html'), name='my_bookings'),
    path('my-reviews/', my_reviews, name='my_reviews'),
    path('my-favourites/', my_favourites, name='my_favourites'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('logout/', logout_view, name='logout'),
    path('post_create/', post_create, name='post_create'),
    path('store_create/', store_create, name='store_create'),
    path('script_room_create/', script_room_create, name='script_room_create'),
    path('booking_create/<int:room_id>/', booking_create, name='booking_create'),
    path('store/<int:store_id>/', store_detail, name='store_detail'),
    path('script/<int:script_id>/', script_detail, name='script_detail'),
    path('review_create/<int:script_id>/', review_create, name='review_create'),
    path('toggle_favourite/<int:script_id>/', toggle_favourite, name='toggle_favourite'),
    path('post/<int:post_id>/', post_detail, name='post_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
