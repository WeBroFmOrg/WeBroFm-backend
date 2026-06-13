from rest_framework import serializers
from .models import Favorite, ContinuePlaying, EpisodeHit, Like, Comment, Report, Feedback
from content.serializers import ShowSerializer, EpisodeSerializer

class FavoriteToggleSerializer(serializers.Serializer):
    show_id = serializers.IntegerField()

class FavoriteSerializer(serializers.ModelSerializer):
    show = ShowSerializer(read_only=True)
    
    class Meta:
        model = Favorite
        fields = ('id', 'show', 'created_at')

class ContinuePlayingSerializer(serializers.ModelSerializer):
    episode = EpisodeSerializer(read_only=True)
    
    class Meta:
        model = ContinuePlaying
        fields = ('id', 'episode', 'last_position_seconds', 'updated_at')

class PlaybackUpdateSerializer(serializers.Serializer):
    episode_id = serializers.IntegerField()
    last_position_seconds = serializers.IntegerField()

class AnalyticsHitSerializer(serializers.Serializer):
    episode_id = serializers.IntegerField()

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'user', 'episode', 'story', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.full_name')
    
    class Meta:
        model = Comment
        fields = ('id', 'username', 'episode', 'story', 'text', 'created_at')
        read_only_fields = ('id', 'username', 'created_at')

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('id', 'ad', 'reason', 'created_at')
        read_only_fields = ('id', 'created_at')

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('id', 'episode', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'created_at')
