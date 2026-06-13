from django.core.cache import cache
from django.db.models import Count, Prefetch
from django.utils import timezone
from datetime import timedelta

from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Author, Show, Episode, Teaser
from .serializers import (
    CategorySerializer, ShowSerializer, EpisodeSerializer,
    PreloadShowSerializer, PreloadEpisodeSerializer, TeaserSerializer
)
from interactions.models import EpisodeHit
from services.storage import storage_service


class PreloadView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            cache_key = "preload_data"
            cached = cache.get(cache_key)
            if cached:
                return Response(cached)
        except Exception:
            pass

        shows = Show.objects.all().select_related('category').prefetch_related(
            'teasers'
        )

        show_ids = [s.id for s in shows]
        episodes = Episode.objects.filter(show_id__in=show_ids).order_by('show', 'sequence_number')
        episode_map = {}
        for ep in episodes:
            episode_map.setdefault(ep.show_id, []).append(ep)
        episode_map = {k: v[:5] for k, v in episode_map.items()}

        categories = Category.objects.filter(is_active=True)

        serialized_shows = []
        for show in shows:
            show_data = PreloadShowSerializer(show).data
            show_data['episodes'] = PreloadEpisodeSerializer(episode_map.get(show.id, []), many=True).data
            serialized_shows.append(show_data)

        data = {
            "shows": serialized_shows,
            "categories": CategorySerializer(categories, many=True).data
        }

        try:
            cache.set(cache_key, data, timeout=300)
        except Exception:
            pass

        return Response(data)


class WeeklyTrendingView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        week_ago = timezone.now() - timedelta(days=7)

        trending_episodes = (
            EpisodeHit.objects
            .filter(created_at__gte=week_ago)
            .values('episode__show')
            .annotate(weekly_hits=Count('id'))
            .order_by('-weekly_hits')[:10]
        )

        episode_ids = [item['episode__show'] for item in trending_episodes]
        shows = Show.objects.filter(id__in=episode_ids).select_related('category', 'author')

        show_dict = {s.id: s for s in shows}
        result = []
        for item in trending_episodes:
            show = show_dict.get(item['episode__show'])
            if show:
                result.append({
                    "id": show.id,
                    "title": show.title,
                    "description": show.description,
                    "thumbnail": str(show.thumbnail),
                    "category_name": show.category.name if show.category else None,
                    "weekly_hits": item['weekly_hits'],
                    "age_rating": show.age_rating,
                    "is_featured": show.is_featured,
                    "created_at": show.created_at
                })

        return Response({"trending": result})


class HomeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cache_key = "home_data"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        categories = Category.objects.filter(is_active=True)
        featured_shows = Show.objects.filter(is_featured=True).select_related('category', 'author')[:5]
        trending_shows = Show.objects.filter(is_trending=True).select_related('category', 'author')[:10]
        recent_shows = Show.objects.order_by('-created_at').select_related('category', 'author')[:10]

        data = {
            "featured": ShowSerializer(featured_shows, many=True).data,
            "trending": ShowSerializer(trending_shows, many=True).data,
            "recent": ShowSerializer(recent_shows, many=True).data,
            "categories": CategorySerializer(categories, many=True).data
        }

        cache.set(cache_key, data, timeout=600)
        return Response(data)


class ShowEpisodesView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EpisodeSerializer

    def get_queryset(self):
        show_id = self.kwargs['show_id']
        return Episode.objects.filter(show_id=show_id).select_related('show')


class EpisodePlayView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, episode_id):
        try:
            episode = Episode.objects.get(id=episode_id)
        except Episode.DoesNotExist:
            return Response({"error": "Episode not found"}, status=status.HTTP_404_NOT_FOUND)

        audio_url = storage_service.generate_signed_url(episode.audio_file_key)
        hls_url = None
        if episode.hls_playlist_key:
            hls_url = storage_service.generate_signed_url(episode.hls_playlist_key)

        return Response({
            "episode_id": episode.id,
            "audio_url": audio_url,
            "hls_url": hls_url,
            "title": episode.title,
            "expires_in": 3600
        })
