from django.db import models
from django.utils.translation import gettext_lazy as _


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True,
        help_text="Short code: en, hi, genz, etc.")
    icon = models.ImageField(upload_to='languages/icons/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = _("Languages")

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='categories/icons/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = _("Categories")

class Author(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='authors/images/', blank=True, null=True)

    def __str__(self):
        return self.name

class Show(models.Model):
    AGE_RATINGS = (
        ('U', 'Universal (All Ages)'),
        ('UA', 'Parental Guidance'),
        ('13+', '13 Plus'),
        ('18+', 'Adults Only'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='shows')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='shows')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True, related_name='shows')
    thumbnail = models.ImageField(upload_to='shows/thumbnails/', blank=True, null=True) # Stored in R2 via custom storage or manual upload
    age_rating = models.CharField(max_length=5, choices=AGE_RATINGS, default='U')
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Episode(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='episodes')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True, related_name='episodes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    audio_file_key = models.CharField(max_length=512, blank=True, help_text="Cloudflare R2 storage key (path)")
    duration_seconds = models.PositiveIntegerField(default=0)
    sequence_number = models.PositiveIntegerField(default=1)
    hls_playlist_key = models.CharField(max_length=512, blank=True, help_text="Path to .m3u8 file in R2")
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sequence_number']

    def __str__(self):
        return f"{self.show.title} - {self.title}"

class EpisodeAnalytics(models.Model):
    episode = models.OneToOneField(Episode, on_delete=models.CASCADE, related_name='analytics')
    total_plays = models.PositiveIntegerField(default=0)
    avg_listen_time = models.FloatField(default=0.0) # in minutes
    completion_rate = models.FloatField(default=0.0) # percentage
    likes = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    
    # JSON field for complex data like retention graph or geographic data
    # (Using TextField for SQLite compatibility if JSONField isn't available, but Django 3.0+ supports it)
    retention_data = models.JSONField(default=dict, help_text="Graph data for listener retention")
    geographic_hits = models.JSONField(default=dict, help_text="Hits per city/region")
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics for {self.episode.title}"

class Teaser(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='teasers/images/', blank=True, null=True)
    sequence = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_converted = models.BooleanField(default=False, help_text="Has been turned into a show")
    converted_show = models.ForeignKey(Show, on_delete=models.SET_NULL, null=True, blank=True, related_name='converted_from_teaser')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sequence']

    def __str__(self):
        return self.title
