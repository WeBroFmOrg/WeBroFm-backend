from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from content.models import Show, Episode


class BinShowListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        shows = Show.objects.filter(is_deleted=True).select_related('category', 'author')
        data = []
        for s in shows:
            ep_count = s.episodes.filter(is_deleted=True).count()
            total_ep = s.episodes.all().count()
            data.append({
                "id": s.id, "title": s.title, "description": s.description,
                "category_name": s.category.name if s.category else None,
                "author_name": s.author.name if s.author else None,
                "deleted_at": s.deleted_at,
                "episodes_in_bin": ep_count,
                "total_episodes": total_ep,
            })
        return Response(data)


class BinShowDetailView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk):
        show = get_object_or_404(Show, pk=pk, is_deleted=True)
        episodes = Episode.objects.filter(show=show)
        return Response({
            "id": show.id, "title": show.title, "description": show.description,
            "deleted_at": show.deleted_at,
            "episodes": [{
                "id": e.id, "title": e.title, "sequence_number": e.sequence_number,
                "is_deleted": e.is_deleted, "deleted_at": e.deleted_at
            } for e in episodes]
        })


class BinShowRestoreView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        show = get_object_or_404(Show, pk=pk, is_deleted=True)
        restore_episodes = request.data.get('restore_episodes', True)
        show.is_deleted = False
        show.deleted_at = None
        show.save()
        if restore_episodes:
            Episode.objects.filter(show=show, is_deleted=True).update(
                is_deleted=False, deleted_at=None
            )
        return Response({"message": "Show restored", "id": show.id})


class BinShowRestoreEpisodesView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        show = get_object_or_404(Show, pk=pk, is_deleted=True)
        episode_ids = request.data.get('episode_ids', [])
        if not episode_ids:
            return Response({"error": "episode_ids required"}, status=400)
        restored = Episode.objects.filter(
            id__in=episode_ids, show=show, is_deleted=True
        ).update(is_deleted=False, deleted_at=None)
        return Response({"message": f"{restored} episodes restored"})


class BinShowPermanentDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, pk):
        show = get_object_or_404(Show, pk=pk, is_deleted=True)
        title = show.title
        show.episodes.all().delete()
        show.delete()
        return Response({"message": f"Show '{title}' permanently deleted"})


class BinEpisodeListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        episodes = Episode.objects.filter(is_deleted=True).select_related('show')
        data = [{
            "id": e.id, "title": e.title, "show_title": e.show.title,
            "show_id": e.show_id, "sequence_number": e.sequence_number,
            "deleted_at": e.deleted_at,
        } for e in episodes]
        return Response(data)


class BinEpisodeRestoreView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        ep = get_object_or_404(Episode, pk=pk, is_deleted=True)
        ep.is_deleted = False
        ep.deleted_at = None
        ep.save()
        return Response({"message": "Episode restored", "id": ep.id})


class BinEpisodePermanentDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, pk):
        ep = get_object_or_404(Episode, pk=pk, is_deleted=True)
        title = ep.title
        ep.delete()
        return Response({"message": f"Episode '{title}' permanently deleted"})


# ── Bulk Actions ──

class BinShowBulkRestoreView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "ids required"}, status=400)
        count = Show.objects.filter(id__in=ids, is_deleted=True).update(
            is_deleted=False, deleted_at=None
        )
        return Response({"message": f"{count} shows restored"})


class BinShowBulkDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "ids required"}, status=400)
        shows = Show.objects.filter(id__in=ids, is_deleted=True)
        count = shows.count()
        Episode.objects.filter(show__in=shows).delete()
        shows.delete()
        return Response({"message": f"{count} shows permanently deleted"})


class BinEpisodeBulkRestoreView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "ids required"}, status=400)
        count = Episode.objects.filter(id__in=ids, is_deleted=True).update(
            is_deleted=False, deleted_at=None
        )
        return Response({"message": f"{count} episodes restored"})


class BinEpisodeBulkDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "ids required"}, status=400)
        count, _ = Episode.objects.filter(id__in=ids, is_deleted=True).delete()
        return Response({"message": f"{count} episodes permanently deleted"})
