from django.db import models
from django.conf import settings
from content.models import Episode, Show

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'show')

class ContinuePlaying(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='playback_history')
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='playback_sessions')
    last_position_seconds = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'episode')
        ordering = ['-updated_at']

class EpisodeHit(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='hits')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    story = models.ForeignKey('collaboration.StorySubmission', on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'episode', 'story')

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    story = models.ForeignKey('collaboration.StorySubmission', on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    text = models.TextField()
    is_active = models.BooleanField(default=True) # For admin moderation
    created_at = models.DateTimeField(auto_now_add=True)

class Report(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ad = models.ForeignKey('collaboration.SponsorshipRequest', on_delete=models.CASCADE, related_name='reports')
    reason = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.PositiveSmallIntegerField(default=5) # 1 to 5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
