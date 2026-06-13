from django.urls import path
from .views import (
    FavoriteToggleView, FavoriteListView, PlaybackUpdateView, 
    ResumeListView, AnalyticsHitView, LikeToggleView,
    CommentListCreateView, FeedbackCreateView, ReportAdView
)

urlpatterns = [
    path('user/favorite/toggle/', FavoriteToggleView.as_view(), name='favorite-toggle'),
    path('user/favorites/', FavoriteListView.as_view(), name='favorite-list'),
    path('user/like/toggle/', LikeToggleView.as_view(), name='like-toggle'),
    path('user/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('user/feedback/', FeedbackCreateView.as_view(), name='feedback-create'),
    path('ads/report/', ReportAdView.as_view(), name='report-ad'),
    path('user/resume/update/', PlaybackUpdateView.as_view(), name='playback-update'),
    path('user/resume/', ResumeListView.as_view(), name='resume-list'),
    path('analytics/hit/', AnalyticsHitView.as_view(), name='analytics-hit'),
]
