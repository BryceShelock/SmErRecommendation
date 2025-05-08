from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta
from surprise import SVD, Dataset, Reader
import pandas as pd
import numpy as np
from .models import UserPreference, UserInteraction, Recommendation
from booking.models import ScriptRoom
from reviews.models import Review

class RecommendationService:
    def __init__(self):
        self.content_weight = 0.4
        self.collaborative_weight = 0.4
        self.popularity_weight = 0.2

    def get_recommendations(self, user, limit=10):
        # Get user preferences
        preferences = UserPreference.objects.get_or_create(user=user)[0]
        
        # Get content-based recommendations
        content_scores = self._get_content_based_scores(user, preferences)
        
        # Get collaborative filtering recommendations
        collaborative_scores = self._get_collaborative_scores(user)
        
        # Get popularity scores
        popularity_scores = self._get_popularity_scores()
        
        # Combine scores
        final_scores = {}
        for script_room in ScriptRoom.objects.all():
            content_score = content_scores.get(script_room.id, 0)
            collaborative_score = collaborative_scores.get(script_room.id, 0)
            popularity_score = popularity_scores.get(script_room.id, 0)
            
            final_score = (
                self.content_weight * content_score +
                self.collaborative_weight * collaborative_score +
                self.popularity_weight * popularity_score
            )
            
            final_scores[script_room.id] = final_score
        
        # Sort and get top recommendations
        sorted_recommendations = sorted(
            final_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        # Create recommendation records
        recommendations = []
        for script_room_id, score in sorted_recommendations:
            script_room = ScriptRoom.objects.get(id=script_room_id)
            reason = self._generate_recommendation_reason(
                script_room,
                content_scores.get(script_room_id, 0),
                collaborative_scores.get(script_room_id, 0),
                popularity_scores.get(script_room_id, 0)
            )
            
            recommendation = Recommendation.objects.create(
                user=user,
                script_room=script_room,
                score=score,
                reason=reason
            )
            recommendations.append(recommendation)
        
        return recommendations

    def _get_content_based_scores(self, user, preferences):
        scores = {}
        for script_room in ScriptRoom.objects.all():
            # Genre match
            genre_score = preferences.genre_weights.get(script_room.genre, 0.5)
            
            # Difficulty match
            difficulty_diff = abs(script_room.difficulty - preferences.difficulty_preference)
            difficulty_score = 1 / (1 + difficulty_diff)
            
            # Price match
            price_range = preferences.price_range
            if price_range:
                min_price = price_range.get('min', 0)
                max_price = price_range.get('max', float('inf'))
                if min_price <= script_room.price <= max_price:
                    price_score = 1
                else:
                    price_score = 0.5
            else:
                price_score = 0.5
            
            # Combine scores
            scores[script_room.id] = (genre_score + difficulty_score + price_score) / 3
        
        return scores

    def _get_collaborative_scores(self, user):
        # Get user interactions
        interactions = UserInteraction.objects.filter(
            user=user,
            timestamp__gte=timezone.now() - timedelta(days=30)
        )
        
        if not interactions.exists():
            return {}
        
        # Create interaction matrix
        interaction_data = []
        for interaction in interactions:
            interaction_data.append({
                'user_id': user.id,
                'script_room_id': interaction.script_room_id,
                'rating': interaction.weight
            })
        
        # Convert to DataFrame
        df = pd.DataFrame(interaction_data)
        
        # Create Surprise dataset
        reader = Reader(rating_scale=(0, 1))
        data = Dataset.load_from_df(df[['user_id', 'script_room_id', 'rating']], reader)
        
        # Train SVD model
        trainset = data.build_full_trainset()
        model = SVD(n_factors=100, n_epochs=20, lr_all=0.005, reg_all=0.02)
        model.fit(trainset)
        
        # Get predictions for all script rooms
        scores = {}
        for script_room in ScriptRoom.objects.all():
            pred = model.predict(user.id, script_room.id)
            scores[script_room.id] = pred.est
        
        return scores

    def _get_popularity_scores(self):
        # Get recent bookings and reviews
        recent_date = timezone.now() - timedelta(days=30)
        
        # Calculate popularity based on bookings and reviews
        popularity_data = ScriptRoom.objects.annotate(
            recent_bookings=Count('booking', filter=models.Q(
                booking__created_at__gte=recent_date
            )),
            recent_reviews=Count('review', filter=models.Q(
                review__created_at__gte=recent_date
            )),
            avg_rating=Avg('review__rating')
        )
        
        # Normalize scores
        max_bookings = max(room.recent_bookings for room in popularity_data)
        max_reviews = max(room.recent_reviews for room in popularity_data)
        max_rating = max(room.avg_rating or 0 for room in popularity_data)
        
        scores = {}
        for room in popularity_data:
            booking_score = room.recent_bookings / max_bookings if max_bookings > 0 else 0
            review_score = room.recent_reviews / max_reviews if max_reviews > 0 else 0
            rating_score = (room.avg_rating or 0) / max_rating if max_rating > 0 else 0
            
            scores[room.id] = (booking_score + review_score + rating_score) / 3
        
        return scores

    def _generate_recommendation_reason(self, script_room, content_score, collaborative_score, popularity_score):
        reasons = []
        
        if content_score > 0.7:
            reasons.append("matches your preferences")
        if collaborative_score > 0.7:
            reasons.append("similar users enjoyed this")
        if popularity_score > 0.7:
            reasons.append("currently trending")
        
        if not reasons:
            reasons.append("based on our analysis")
        
        return f"Recommended because it {', '.join(reasons)}." 