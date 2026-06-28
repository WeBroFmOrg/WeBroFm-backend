from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone

from content.models import Show
from interactions.models import EpisodeHit


class Command(BaseCommand):
    help = "Calculate all-time trending ranking and cache it for 12 hours"

    CACHE_KEY = "trending_ranking"
    LIMIT = 20

    def handle(self, *args, **options):
        self.stdout.write(f"[{timezone.now():%Y-%m-%d %H:%M:%S}] Calculating trending ranking...")

        hits_per_show = (
            EpisodeHit.objects
            .values('episode__show')
            .annotate(total_hits=Count('id'))
            .order_by('-total_hits')[:self.LIMIT]
        )

        show_ids = [item['episode__show'] for item in hits_per_show]
        shows = Show.objects.filter(id__in=show_ids).select_related('category', 'author')
        show_dict = {s.id: s for s in shows}

        result = []
        for rank, item in enumerate(hits_per_show, start=1):
            show = show_dict.get(item['episode__show'])
            if show:
                item['total_hits']
                result.append({
                    "rank": rank,
                    "id": show.id,
                    "title": show.title,
                    "description": show.description,
                    "thumbnail": str(show.thumbnail),
                    "category_name": show.category.name if show.category else None,
                    "total_hits": item['total_hits'],
                    "age_rating": show.age_rating,
                    "is_featured": show.is_featured,
                    "created_at": show.created_at.isoformat(),
                    "_cached_at": timezone.now().isoformat(),
                })

        try:
            cache.set(self.CACHE_KEY, result, timeout=None)
            self.stdout.write(self.style.SUCCESS(f"Trending ranking cached: {len(result)} shows"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to cache: {e}"))
