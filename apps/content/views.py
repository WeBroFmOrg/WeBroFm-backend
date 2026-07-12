from django.core.cache import cache
from django.db.models import Count, Prefetch
from django.utils import timezone
from datetime import timedelta

from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Author, Show, Episode, Teaser, Language
from .serializers import (
    CategorySerializer, ShowSerializer, EpisodeSerializer,
    PreloadShowSerializer, PreloadEpisodeSerializer, TeaserSerializer,
    LanguageSerializer
)
from interactions.models import EpisodeHit
from services.storage import storage_service


class PreloadView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        language_code = request.query_params.get('language')

        try:
            cache_key = f"preload_data_{language_code or 'all'}"
            cached = cache.get(cache_key)
            if cached:
                return Response(cached)
        except Exception:
            pass

        shows = Show.objects.filter(is_deleted=False).select_related('category', 'language')
        if language_code:
            shows = shows.filter(language__code=language_code)

        show_ids = [s.id for s in shows]
        episodes = Episode.objects.filter(show_id__in=show_ids).order_by('show', 'sequence_number')
        if language_code:
            episodes = episodes.filter(language__code=language_code)
        episode_map = {}
        for ep in episodes:
            episode_map.setdefault(ep.show_id, []).append(ep)
        episode_map = {k: v[:5] for k, v in episode_map.items()}

        categories = Category.objects.filter(is_active=True)
        languages = Language.objects.filter(is_active=True)

        serialized_shows = []
        for show in shows:
            show_data = PreloadShowSerializer(show).data
            show_data['episodes'] = PreloadEpisodeSerializer(episode_map.get(show.id, []), many=True).data
            serialized_shows.append(show_data)

        teasers = Teaser.objects.filter(is_active=True, is_converted=False)
        data = {
            "shows": serialized_shows,
            "categories": CategorySerializer(categories, many=True).data,
            "languages": LanguageSerializer(languages, many=True).data,
            "teasers": TeaserSerializer(teasers, many=True).data
        }

        try:
            cache.set(cache_key, data, timeout=300)
        except Exception:
            pass

        return Response(data)


class WeeklyTrendingView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        language_code = request.query_params.get('language')

        cache_key = f"trending_ranking_{language_code or 'all'}"
        cached = cache.get(cache_key)
        if cached:
            return Response({"trending": cached, "cached": True, "updated_at": cached[0].get('_cached_at') if cached else None})

        trending = self._calculate_ranking(language_code=language_code)
        try:
            cache.set(cache_key, trending, timeout=43200)
        except Exception:
            pass
        return Response({"trending": trending})

    @staticmethod
    def _calculate_ranking(limit=20, language_code=None):
        hits = EpisodeHit.objects.values('episode__show').annotate(total_hits=Count('id')).order_by('-total_hits')[:limit * 2]

        show_ids = [item['episode__show'] for item in hits]
        shows_qs = Show.objects.filter(id__in=show_ids, is_deleted=False).select_related('category', 'author', 'language')
        if language_code:
            shows_qs = shows_qs.filter(language__code=language_code)

        shows = shows_qs[:limit]
        show_dict = {s.id: s for s in shows}

        result = []
        for rank, item in enumerate(hits, start=1):
            show = show_dict.get(item['episode__show'])
            if show and len(result) < limit:
                result.append({
                    "rank": rank,
                    "id": show.id,
                    "title": show.title,
                    "description": show.description,
                    "thumbnail": str(show.thumbnail),
                    "category_name": show.category.name if show.category else None,
                    "language_name": show.language.name if show.language else None,
                    "language_code": show.language.code if show.language else None,
                    "total_hits": item['total_hits'],
                    "age_rating": show.age_rating,
                    "is_featured": show.is_featured,
                    "created_at": show.created_at
                })
        return result


class HomeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        language_code = request.query_params.get('language')

        cache_key = f"home_data_{language_code or 'all'}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        base_qs = Show.objects.filter(is_deleted=False).select_related('category', 'author', 'language')
        if language_code:
            base_qs = base_qs.filter(language__code=language_code)

        categories = Category.objects.filter(is_active=True)
        languages = Language.objects.filter(is_active=True)
        featured_shows = base_qs.filter(is_featured=True)[:5]
        trending_shows = base_qs.filter(is_trending=True)[:10]
        recent_shows = base_qs.order_by('-created_at')[:10]

        data = {
            "featured": ShowSerializer(featured_shows, many=True).data,
            "trending": ShowSerializer(trending_shows, many=True).data,
            "recent": ShowSerializer(recent_shows, many=True).data,
            "categories": CategorySerializer(categories, many=True).data,
            "languages": LanguageSerializer(languages, many=True).data,
        }

        cache.set(cache_key, data, timeout=600)
        return Response(data)


class ShowEpisodesView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EpisodeSerializer

    def get_queryset(self):
        show_id = self.kwargs['show_id']
        qs = Episode.objects.filter(show_id=show_id, is_deleted=False).select_related('show', 'language')
        language_code = self.request.query_params.get('language')
        if language_code:
            qs = qs.filter(language__code=language_code)
        return qs



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
