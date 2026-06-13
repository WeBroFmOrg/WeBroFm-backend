from django.urls import path
from .views import StorySubmitView, UserStoryListView, SponsorshipSubmitView, UserSponsorshipListView

urlpatterns = [
    path('collab/story/submit/', StorySubmitView.as_view(), name='story-submit'),
    path('collab/stories/', UserStoryListView.as_view(), name='user-stories'),
    path('collab/ads/submit/', SponsorshipSubmitView.as_view(), name='ad-submit'),
    path('collab/ads/', UserSponsorshipListView.as_view(), name='user-ads'),
]
