from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .admin_views import (
    AdminLoginView, DashboardStatsView,
    AdminUserListView, AdminUserDetailView, AdminUserActionView,
    AdminCategoryListCreateView, AdminCategoryDetailView,
    AdminAuthorListCreateView, AdminAuthorDetailView,
    AdminShowListCreateView, AdminShowDetailView,
    AdminEpisodeListCreateView, AdminEpisodeDetailView,
    AdminEpisodeAnalyticsView,
    AdminCommentListView, AdminCommentManageView,
    AdminReportListView, AdminReportResolveView,
    AdminFeedbackListView,
    AdminStoryListView, AdminStoryDetailView, AdminCollabActionView,
    AdminSponsorshipListView, AdminSponsorshipDetailView, AdminSponsorshipActionView,
    AdminR2ExplorerView, AdminR2UploadView, AdminR2DeleteView,
    AdminLikesListView, AdminFavoritesListView,
)

urlpatterns = [
    # Auth
    path('admin/login/', csrf_exempt(AdminLoginView.as_view()), name='admin-login'),

    # Dashboard
    path('admin/dashboard/stats/', DashboardStatsView.as_view(), name='admin-stats'),

    # Users
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/<int:user_id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/users/<int:user_id>/action/', AdminUserActionView.as_view(), name='admin-user-action'),

    # Categories
    path('admin/categories/', AdminCategoryListCreateView.as_view(), name='admin-category-list'),
    path('admin/categories/<int:pk>/', AdminCategoryDetailView.as_view(), name='admin-category-detail'),

    # Authors
    path('admin/authors/', AdminAuthorListCreateView.as_view(), name='admin-author-list'),
    path('admin/authors/<int:pk>/', AdminAuthorDetailView.as_view(), name='admin-author-detail'),

    # Shows
    path('admin/shows/', AdminShowListCreateView.as_view(), name='admin-show-list'),
    path('admin/shows/<int:pk>/', AdminShowDetailView.as_view(), name='admin-show-detail'),

    # Episodes
    path('admin/episodes/', AdminEpisodeListCreateView.as_view(), name='admin-episode-list'),
    path('admin/episodes/<int:pk>/', AdminEpisodeDetailView.as_view(), name='admin-episode-detail'),

    # Episode Analytics
    path('admin/episodes/<int:episode_id>/analytics/', AdminEpisodeAnalyticsView.as_view(), name='admin-episode-analytics'),

    # Comments
    path('admin/comments/', AdminCommentListView.as_view(), name='admin-comment-list'),
    path('admin/comments/<int:comment_id>/', AdminCommentManageView.as_view(), name='admin-comment-manage'),

    # Reports
    path('admin/reports/', AdminReportListView.as_view(), name='admin-report-list'),
    path('admin/reports/<int:report_id>/resolve/', AdminReportResolveView.as_view(), name='admin-report-resolve'),

    # Feedback
    path('admin/feedback/', AdminFeedbackListView.as_view(), name='admin-feedback-list'),

    # Stories / Collab
    path('admin/stories/', AdminStoryListView.as_view(), name='admin-story-list'),
    path('admin/stories/<int:pk>/', AdminStoryDetailView.as_view(), name='admin-story-detail'),
    path('admin/collab/<int:collab_id>/action/', AdminCollabActionView.as_view(), name='admin-collab-action'),

    # Sponsorships
    path('admin/sponsorships/', AdminSponsorshipListView.as_view(), name='admin-sponsorship-list'),
    path('admin/sponsorships/<int:pk>/', AdminSponsorshipDetailView.as_view(), name='admin-sponsorship-detail'),
    path('admin/sponsorships/<int:sponsorship_id>/action/', AdminSponsorshipActionView.as_view(), name='admin-sponsorship-action'),

    # R2 Storage
    path('admin/storage/explorer/', AdminR2ExplorerView.as_view(), name='admin-storage-explorer'),
    path('admin/storage/upload/', AdminR2UploadView.as_view(), name='admin-storage-upload'),
    path('admin/storage/delete/', AdminR2DeleteView.as_view(), name='admin-storage-delete'),

    # Content data (read-only admin views)
    path('admin/likes/', AdminLikesListView.as_view(), name='admin-likes-list'),
    path('admin/favorites/', AdminFavoritesListView.as_view(), name='admin-favorites-list'),
]
