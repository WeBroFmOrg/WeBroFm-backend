import os
import io
import uuid
import tempfile
from datetime import datetime, timedelta

from django.db.models import Count, Sum, Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

from rest_framework import status, permissions, generics, parsers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from PIL import Image

from accounts.models import CustomUser
from accounts.serializers import UserSerializer
from content.models import Show, Episode, Category, Author, EpisodeAnalytics, Teaser
from content.serializers import (
    ShowSerializer, EpisodeSerializer, EpisodeDetailSerializer,
    CategorySerializer, AuthorSerializer, EpisodeAnalyticsSerializer,
    TeaserSerializer
)
from interactions.models import EpisodeHit, Comment, Report, Feedback, Like, Favorite, ContinuePlaying
from interactions.serializers import (
    CommentSerializer, ReportSerializer, FeedbackSerializer,
    LikeSerializer, FavoriteSerializer, ContinuePlayingSerializer
)
from collaboration.models import StorySubmission, SponsorshipRequest
from collaboration.serializers import StorySubmissionSerializer, SponsorshipRequestSerializer
from services.storage import storage_service


# ──────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────

@method_decorator(csrf_exempt, name='dispatch')
class AdminLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        user = authenticate(username=phone_number, password=password)
        if user and user.is_staff:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'full_name': user.full_name,
                    'phone_number': user.phone_number,
                    'is_superuser': user.is_superuser
                }
            })
        return Response({"error": "Invalid credentials or not an admin"}, status=401)


# ──────────────────────────────────────────────
# DASHBOARD STATS
# ──────────────────────────────────────────────

class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total_users = CustomUser.objects.count()
        total_shows = Show.objects.count()
        total_episodes = Episode.objects.count()
        total_hits = EpisodeHit.objects.count()
        total_categories = Category.objects.count()
        total_authors = Author.objects.count()
        total_comments = Comment.objects.count()
        total_feedback = Feedback.objects.count()
        pending_stories = StorySubmission.objects.filter(status='pending').count()
        pending_ads = SponsorshipRequest.objects.filter(status='pending').count()

        # Last 7 days activity
        week_ago = datetime.now() - timedelta(days=7)
        weekly_hits = EpisodeHit.objects.filter(created_at__gte=week_ago).count()
        weekly_users = CustomUser.objects.filter(date_joined__gte=week_ago).count()

        # Shows per category
        category_data = Category.objects.annotate(show_count=Count('shows')).values('name', 'show_count')

        return Response({
            "summary": {
                "users": total_users,
                "shows": total_shows,
                "episodes": total_episodes,
                "hits": total_hits,
                "categories": total_categories,
                "authors": total_authors,
                "comments": total_comments,
                "feedback": total_feedback,
                "pending_stories": pending_stories,
                "pending_ads": pending_ads,
                "weekly_hits": weekly_hits,
                "weekly_new_users": weekly_users
            },
            "categories": category_data
        })


# ──────────────────────────────────────────────
# USERS - Full CRUD
# ──────────────────────────────────────────────

class AdminUserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(phone_number__icontains=search) |
                Q(full_name__icontains=search) |
                Q(email__icontains=search)
            )
        return qs


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'user_id'


class AdminUserActionView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, user_id):
        action = request.data.get('action')
        user = get_object_or_404(CustomUser, id=user_id)

        if action == 'block':
            user.is_active = False
            user.save()
            return Response({"message": "User blocked", "is_active": False})
        elif action == 'activate':
            user.is_active = True
            user.save()
            return Response({"message": "User activated", "is_active": True})
        elif action == 'make_staff':
            user.is_staff = True
            user.save()
            return Response({"message": "User made staff", "is_staff": True})
        elif action == 'remove_staff':
            user.is_staff = False
            user.save()
            return Response({"message": "Staff access removed", "is_staff": False})
        return Response({"error": "Invalid action"}, status=400)


# ──────────────────────────────────────────────
# CATEGORIES - Full CRUD
# ──────────────────────────────────────────────

class AdminCategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


# ──────────────────────────────────────────────
# AUTHORS - Full CRUD
# ──────────────────────────────────────────────

class AdminAuthorListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Author.objects.all().order_by('name')
    serializer_class = AuthorSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


class AdminAuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


# ──────────────────────────────────────────────
# SHOWS - Full CRUD
# ──────────────────────────────────────────────

class AdminShowListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Show.objects.all().select_related('category', 'author').order_by('-created_at')
    serializer_class = ShowSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        category_id = self.request.query_params.get('category')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs


class AdminShowDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Show.objects.all().select_related('category', 'author')
    serializer_class = ShowSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


# ──────────────────────────────────────────────
# EPISODES - Full CRUD
# ──────────────────────────────────────────────

class AdminEpisodeListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Episode.objects.all().select_related('show').order_by('show', 'sequence_number')
    serializer_class = EpisodeSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        qs = super().get_queryset()
        show_id = self.request.query_params.get('show')
        if show_id:
            qs = qs.filter(show_id=show_id)
        return qs


class AdminEpisodeDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Episode.objects.all().select_related('show')
    serializer_class = EpisodeDetailSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


class AdminEpisodePlayView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk):
        from django.http import HttpResponseRedirect
        from services.storage import storage_service
        episode = get_object_or_404(Episode, pk=pk)
        if not episode.audio_file_key:
            return Response({"error": "No audio file"}, status=404)
        url = storage_service.generate_signed_url(episode.audio_file_key)
        if not url:
            return Response({"error": "Failed to generate URL"}, status=500)
        return HttpResponseRedirect(url)


# ──────────────────────────────────────────────
# EPISODE ANALYTICS
# ──────────────────────────────────────────────

class AdminEpisodeAnalyticsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, episode_id):
        analytics = get_object_or_404(EpisodeAnalytics, episode_id=episode_id)
        serializer = EpisodeAnalyticsSerializer(analytics)
        return Response(serializer.data)

    def put(self, request, episode_id):
        analytics, _ = EpisodeAnalytics.objects.get_or_create(episode_id=episode_id)
        serializer = EpisodeAnalyticsSerializer(analytics, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


# ──────────────────────────────────────────────
# COMMENTS - Full CRUD
# ──────────────────────────────────────────────

class AdminCommentListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Comment.objects.all().select_related('user', 'episode', 'story').order_by('-created_at')
    serializer_class = CommentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        episode_id = self.request.query_params.get('episode')
        if episode_id:
            qs = qs.filter(episode_id=episode_id)
        return qs


class AdminCommentManageView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        comment.delete()
        return Response({"message": "Comment removed"})

    def patch(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        is_active = request.data.get('is_active')
        if is_active is not None:
            comment.is_active = is_active
            comment.save()
        return Response({"message": "Comment updated", "is_active": comment.is_active})


# ──────────────────────────────────────────────
# REPORTS
# ──────────────────────────────────────────────

class AdminReportListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Report.objects.all().select_related('user', 'ad').order_by('-created_at')
    serializer_class = ReportSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        resolved = self.request.query_params.get('resolved')
        if resolved == 'true':
            qs = qs.filter(is_resolved=True)
        elif resolved == 'false':
            qs = qs.filter(is_resolved=False)
        return qs


class AdminReportResolveView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, report_id):
        report = get_object_or_404(Report, id=report_id)
        report.is_resolved = True
        report.save()
        return Response({"message": "Report resolved"})


# ──────────────────────────────────────────────
# FEEDBACK
# ──────────────────────────────────────────────

class AdminFeedbackListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Feedback.objects.all().select_related('user', 'episode').order_by('-created_at')
    serializer_class = FeedbackSerializer


# ──────────────────────────────────────────────
# STORIES / COLLAB - Full CRUD
# ──────────────────────────────────────────────

class AdminStoryListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = StorySubmission.objects.all().select_related('user').order_by('-created_at')
    serializer_class = StorySubmissionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class AdminStoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = StorySubmission.objects.all()
    serializer_class = StorySubmissionSerializer


class AdminCollabActionView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, collab_id):
        action = request.data.get('action')
        reason = request.data.get('reason', '')
        collab = get_object_or_404(StorySubmission, id=collab_id)

        if action == 'approve':
            collab.status = 'approved'
        elif action == 'reject':
            collab.status = 'rejected'
            collab.rejection_reason = reason
        elif action == 'reviewing':
            collab.status = 'reviewing'
        else:
            return Response({"error": "Invalid action"}, status=400)

        collab.save()
        return Response({"status": collab.status, "message": f"Story {action}d"})


# ──────────────────────────────────────────────
# SPONSORSHIPS - Full CRUD
# ──────────────────────────────────────────────

class AdminSponsorshipListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = SponsorshipRequest.objects.all().select_related('user').order_by('-created_at')
    serializer_class = SponsorshipRequestSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class AdminSponsorshipDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = SponsorshipRequest.objects.all()
    serializer_class = SponsorshipRequestSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


class AdminSponsorshipActionView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, sponsorship_id):
        action = request.data.get('action')
        reason = request.data.get('reason', '')
        sponsorship = get_object_or_404(SponsorshipRequest, id=sponsorship_id)

        if action == 'approve':
            sponsorship.status = 'approved'
        elif action == 'reject':
            sponsorship.status = 'rejected'
            sponsorship.rejection_reason = reason
        elif action == 'expire':
            sponsorship.status = 'expired'
        else:
            return Response({"error": "Invalid action"}, status=400)

        sponsorship.save()
        return Response({"status": sponsorship.status, "message": f"Ad {action}d"})


# ──────────────────────────────────────────────
# TEASERS - Full CRUD
# ──────────────────────────────────────────────

class AdminTeaserListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Teaser.objects.all().order_by('sequence')
    serializer_class = TeaserSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


class AdminTeaserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Teaser.objects.all()
    serializer_class = TeaserSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


class AdminTeaserConvertToShowView(APIView):
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def post(self, request, pk):
        teaser = get_object_or_404(Teaser, pk=pk)
        if teaser.is_converted:
            return Response({"error": "Teaser already converted to a show"}, status=400)

        category_id = request.data.get('category')
        author_id = request.data.get('author')
        description = request.data.get('description', '')

        if not category_id or not author_id:
            return Response({"error": "category and author are required"}, status=400)

        from content.models import Show
        from django.core.files.storage import default_storage
        import uuid, os

        # Copy teaser image to show thumbnail path if it exists
        thumbnail = None
        if teaser.image:
            try:
                ext = os.path.splitext(teaser.image.name)[1].lower()
                new_key = f"shows/thumbnails/{uuid.uuid4().hex}{ext}"
                img_file = default_storage.open(teaser.image.name)
                default_storage.save(new_key, img_file)
                thumbnail = new_key
            except Exception:
                pass

        show = Show.objects.create(
            title=teaser.title,
            description=description,
            category_id=category_id,
            author_id=author_id,
            thumbnail=thumbnail,
            age_rating='U'
        )

        teaser.is_converted = True
        teaser.converted_show = show
        teaser.save()

        from content.serializers import ShowSerializer
        return Response({
            "message": "Show created from teaser",
            "show": ShowSerializer(show).data,
            "teaser": TeaserSerializer(teaser).data
        }, status=201)


# ──────────────────────────────────────────────
# R2 STORAGE MANAGEMENT - Upload / Explorer / Delete
# ──────────────────────────────────────────────

class AdminR2ExplorerView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        prefix = request.query_params.get('prefix', '')
        data = storage_service.list_files(prefix)
        return Response(data)


class AdminR2UploadView(APIView):
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided"}, status=400)

        prefix = request.data.get('prefix', 'uploads/')
        compress = request.data.get('compress', 'true').lower() == 'true'

        # Generate unique filename
        ext = os.path.splitext(file.name)[1].lower()
        unique_name = f"{uuid.uuid4().hex}{ext}"
        object_key = f"{prefix.rstrip('/')}/{unique_name}"

        # Image compression (if compress=True and file is an image)
        if compress and ext in ('.jpg', '.jpeg', '.png', '.webp'):
            try:
                img = Image.open(file)
                img_format = 'JPEG' if ext in ('.jpg', '.jpeg') else 'PNG' if ext == '.png' else 'WEBP'

                # Resize if larger than 1920px on longest side
                if max(img.size) > 1920:
                    ratio = 1920 / max(img.size)
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    img = img.resize(new_size, Image.LANCZOS)

                # Compress
                output = io.BytesIO()
                if img_format == 'JPEG':
                    img.save(output, format=img_format, quality=80, optimize=True)
                elif img_format == 'PNG':
                    img.save(output, format=img_format, optimize=True)
                else:
                    img.save(output, format=img_format, quality=80)

                output.seek(0)
                file = InMemoryUploadedFile(
                    output, 'file', unique_name, file.content_type,
                    output.getbuffer().nbytes, None
                )
            except Exception as e:
                return Response({"error": f"Compression failed: {str(e)}"}, status=400)

        # Upload to R2 via django-storages (default storage)
        from django.core.files.storage import default_storage
        try:
            saved_path = default_storage.save(object_key, file)
            url = storage_service.generate_signed_url(saved_path)
            return Response({
                "message": "File uploaded successfully",
                "key": saved_path,
                "url": url,
                "size": file.size,
                "compressed": compress and ext in ('.jpg', '.jpeg', '.png', '.webp')
            }, status=201)
        except Exception as e:
            return Response({"error": f"Upload failed: {str(e)}"}, status=500)


class AdminR2DeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request):
        key = request.data.get('key') or request.query_params.get('key')
        if not key:
            return Response({"error": "No key provided"}, status=400)

        try:
            from django.core.files.storage import default_storage
            default_storage.delete(key)
            return Response({"message": f"Deleted {key}"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# ──────────────────────────────────────────────
# LIKES / FAVORITES / CONTINUE PLAYING (Admin Read)
# ──────────────────────────────────────────────

class AdminLikesListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Like.objects.all().select_related('user', 'episode').order_by('-created_at')
    serializer_class = LikeSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        episode_id = self.request.query_params.get('episode')
        if episode_id:
            qs = qs.filter(episode_id=episode_id)
        return qs


class AdminFavoritesListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Favorite.objects.all().select_related('user', 'show').order_by('-created_at')
    serializer_class = FavoriteSerializer
