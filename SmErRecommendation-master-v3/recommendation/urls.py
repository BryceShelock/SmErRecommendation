from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'preferences', views.UserPreferenceViewSet, basename='preference')
router.register(r'interactions', views.UserInteractionViewSet, basename='interaction')
router.register(r'recommendations', views.RecommendationViewSet, basename='recommendation')

urlpatterns = [
    path('', include(router.urls)),
] 