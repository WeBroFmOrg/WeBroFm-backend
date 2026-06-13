from django.urls import path
from .views import HomeView, ShowEpisodesView, EpisodePlayView, PreloadView, WeeklyTrendingView

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('home/preload/', PreloadView.as_view(), name='preload'),
    path('home/trending/', WeeklyTrendingView.as_view(), name='weekly-trending'),
    path('shows/<int:show_id>/episodes/', ShowEpisodesView.as_view(), name='show-episodes'),
    path('play/ep/<int:episode_id>/', EpisodePlayView.as_view(), name='episode-play'),
]
