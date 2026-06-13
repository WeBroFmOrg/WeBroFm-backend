from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import Favorite, ContinuePlaying, EpisodeHit, Like, Comment, Report, Feedback
from .serializers import (
    FavoriteToggleSerializer, FavoriteSerializer, 
    ContinuePlayingSerializer, PlaybackUpdateSerializer, 
    AnalyticsHitSerializer, LikeSerializer, CommentSerializer,
    ReportSerializer, FeedbackSerializer
)
from content.models import Show, Episode

class FavoriteToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = FavoriteToggleSerializer(data=request.data)
        if serializer.is_valid():
            show_id = serializer.validated_data['show_id']
            show = get_object_or_404(Show, id=show_id)
            
            favorite, created = Favorite.objects.get_or_create(user=request.user, show=show)
            if not created:
                favorite.delete()
                return Response({"message": "Show removed from favorites", "favorited": False}, status=status.HTTP_200_OK)
            
            return Response({"message": "Show added to favorites", "favorited": True}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        episode_id = request.data.get('episode_id')
        story_id = request.data.get('story_id')
        
        if episode_id:
            target = {"episode_id": episode_id}
        elif story_id:
            target = {"story_id": story_id}
        else:
            return Response({"error": "episode_id or story_id required"}, status=status.HTTP_400_BAD_REQUEST)

        like, created = Like.objects.get_or_create(user=request.user, **target)
        if not created:
            like.delete()
            return Response({"liked": False})
        return Response({"liked": True}, status=status.HTTP_201_CREATED)

class CommentListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        episode_id = self.request.query_params.get('episode_id')
        story_id = self.request.query_params.get('story_id')
        if episode_id:
            return Comment.objects.filter(episode_id=episode_id, is_active=True).select_related('user')
        if story_id:
            return Comment.objects.filter(story_id=story_id, is_active=True).select_related('user')
        return Comment.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReportAdView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReportSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FeedbackCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FeedbackSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Keep original views...
class FavoriteListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FavoriteSerializer
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('show')

class PlaybackUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        serializer = PlaybackUpdateSerializer(data=request.data)
        if serializer.is_valid():
            episode_id = serializer.validated_data['episode_id']
            last_position = serializer.validated_data['last_position_seconds']
            episode = get_object_or_404(Episode, id=episode_id)
            ContinuePlaying.objects.update_or_create(
                user=request.user, episode=episode,
                defaults={'last_position_seconds': last_position}
            )
            return Response({"message": "Updated"})
        return Response(serializer.errors, status=400)

class ResumeListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContinuePlayingSerializer
    def get_queryset(self):
        return ContinuePlaying.objects.filter(user=self.request.user).select_related('episode', 'episode__show')

class AnalyticsHitView(APIView):
    # This might be used by mobile app to track hits
    def post(self, request):
        serializer = AnalyticsHitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "recorded"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
