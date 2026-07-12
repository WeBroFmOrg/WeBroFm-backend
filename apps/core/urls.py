from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .admin_views import (
    AdminLoginView, DashboardStatsView,
    AdminUserListView, AdminUserDetailView, AdminUserActionView,
    AdminCategoryListCreateView, AdminCategoryDetailView,
    AdminLanguageListCreateView, AdminLanguageDetailView,
    AdminAuthorListCreateView, AdminAuthorDetailView,
    AdminShowListCreateView, AdminShowDetailView,
    AdminEpisodeListCreateView, AdminEpisodeDetailView, AdminEpisodePlayView,
    AdminEpisodeAnalyticsView,
    AdminTeaserListCreateView, AdminTeaserDetailView, AdminTeaserConvertToShowView,
    AdminCommentListView, AdminCommentManageView,
    AdminReportListView, AdminReportResolveView,
    AdminFeedbackListView,
    AdminStoryListView, AdminStoryDetailView, AdminCollabActionView,
    AdminSponsorshipListView, AdminSponsorshipDetailView, AdminSponsorshipActionView,
    AdminR2ExplorerView, AdminR2UploadView, AdminR2DeleteView,
    AdminLikesListView, AdminFavoritesListView,
)
from .bin_views import (
    BinShowListView, BinShowDetailView,
    BinShowRestoreView, BinShowRestoreEpisodesView, BinShowPermanentDeleteView,
    BinEpisodeListView, BinEpisodeRestoreView, BinEpisodePermanentDeleteView,
    BinShowBulkRestoreView, BinShowBulkDeleteView,
    BinEpisodeBulkRestoreView, BinEpisodeBulkDeleteView,
)
from .employee_views import (
    EmployeeLoginView, EmployeeListCreateView, EmployeeDetailView, EmployeeToggleView,
    AvailablePermissionsView,
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

    # Languages
    path('admin/languages/', AdminLanguageListCreateView.as_view(), name='admin-language-list'),
    path('admin/languages/<int:pk>/', AdminLanguageDetailView.as_view(), name='admin-language-detail'),

    # Authors
    path('admin/authors/', AdminAuthorListCreateView.as_view(), name='admin-author-list'),
    path('admin/authors/<int:pk>/', AdminAuthorDetailView.as_view(), name='admin-author-detail'),

    # Shows
    path('admin/shows/', AdminShowListCreateView.as_view(), name='admin-show-list'),
    path('admin/shows/<int:pk>/', AdminShowDetailView.as_view(), name='admin-show-detail'),

    # Episodes
    path('admin/episodes/', AdminEpisodeListCreateView.as_view(), name='admin-episode-list'),
    path('admin/episodes/<int:pk>/', AdminEpisodeDetailView.as_view(), name='admin-episode-detail'),

    # Episode Play / Analytics
    path('admin/episodes/<int:pk>/play/', AdminEpisodePlayView.as_view(), name='admin-episode-play'),
    path('admin/episodes/<int:episode_id>/analytics/', AdminEpisodeAnalyticsView.as_view(), name='admin-episode-analytics'),

    # Teasers
    path('admin/teasers/', AdminTeaserListCreateView.as_view(), name='admin-teaser-list'),
    path('admin/teasers/<int:pk>/', AdminTeaserDetailView.as_view(), name='admin-teaser-detail'),
    path('admin/teasers/<int:pk>/convert-to-show/', AdminTeaserConvertToShowView.as_view(), name='admin-teaser-convert'),

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

    # ── Recycle Bin ──
    path('admin/bin/shows/', BinShowListView.as_view(), name='bin-show-list'),
    path('admin/bin/shows/<int:pk>/', BinShowDetailView.as_view(), name='bin-show-detail'),
    path('admin/bin/shows/<int:pk>/restore/', BinShowRestoreView.as_view(), name='bin-show-restore'),
    path('admin/bin/shows/<int:pk>/restore-episodes/', BinShowRestoreEpisodesView.as_view(), name='bin-show-restore-episodes'),
    path('admin/bin/shows/<int:pk>/permanent/', BinShowPermanentDeleteView.as_view(), name='bin-show-permanent-delete'),
    path('admin/bin/shows/bulk-restore/', BinShowBulkRestoreView.as_view(), name='bin-show-bulk-restore'),
    path('admin/bin/shows/bulk-delete/', BinShowBulkDeleteView.as_view(), name='bin-show-bulk-delete'),
    path('admin/bin/episodes/', BinEpisodeListView.as_view(), name='bin-episode-list'),
    path('admin/bin/episodes/<int:pk>/restore/', BinEpisodeRestoreView.as_view(), name='bin-episode-restore'),
    path('admin/bin/episodes/<int:pk>/permanent/', BinEpisodePermanentDeleteView.as_view(), name='bin-episode-permanent-delete'),
    path('admin/bin/episodes/bulk-restore/', BinEpisodeBulkRestoreView.as_view(), name='bin-episode-bulk-restore'),
    path('admin/bin/episodes/bulk-delete/', BinEpisodeBulkDeleteView.as_view(), name='bin-episode-bulk-delete'),

    # ── Employee Management (RBAC) ──
    path('admin/employee-login/', EmployeeLoginView.as_view(), name='employee-login'),
    path('admin/employees/', EmployeeListCreateView.as_view(), name='employee-list'),
    path('admin/employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('admin/employees/<int:pk>/toggle/', EmployeeToggleView.as_view(), name='employee-toggle'),
    path('admin/employees/permissions-list/', AvailablePermissionsView.as_view(), name='employee-permissions-list'),
]
