from django.urls import path
from .views import GenderBasedRecommendationViewSet

urlpatterns = [
    path('recommend/', GenderBasedRecommendationViewSet.as_view({'get': 'recommend'}), name='gender-based-recommendation'),
]