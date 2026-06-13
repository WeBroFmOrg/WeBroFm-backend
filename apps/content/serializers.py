from rest_framework import serializers
from .models import Category, Author, Show, Episode, Teaser

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'icon')

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('id', 'name', 'bio', 'image')

class ShowSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    author_name = serializers.ReadOnlyField(source='author.name')
    
    class Meta:
        model = Show
        fields = (
            'id', 'title', 'description', 'category', 'author', 
            'category_name', 'author_name', 'thumbnail', 
            'age_rating', 'is_featured', 'is_trending', 'created_at'
        )
        extra_kwargs = {
            'category': {'write_only': True},
            'author': {'write_only': True},
        }

class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = ('id', 'show', 'title', 'description', 'duration_seconds', 'sequence_number', 'created_at')

class EpisodeDetailSerializer(EpisodeSerializer):
    class Meta(EpisodeSerializer.Meta):
        fields = EpisodeSerializer.Meta.fields + ('audio_file_key', 'hls_playlist_key')

class EpisodeAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = '__all__'

class TeaserSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Teaser
        fields = ('id', 'show', 'title', 'video_key', 'thumbnail_key', 'video_url', 'thumbnail_url', 'duration_seconds', 'sequence')

    def get_video_url(self, obj):
        from services.storage import storage_service
        if obj.video_key:
            try:
                return storage_service.generate_signed_url(obj.video_key)
            except Exception:
                return None
        return None

    def get_thumbnail_url(self, obj):
        from services.storage import storage_service
        if obj.thumbnail_key:
            try:
                return storage_service.generate_signed_url(obj.thumbnail_key)
            except Exception:
                return None
        return None

class PreloadEpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = ('id', 'title', 'sequence_number', 'duration_seconds', 'audio_file_key', 'hls_playlist_key')

class PreloadShowSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    thumbnail_url = serializers.SerializerMethodField()
    teasers = TeaserSerializer(many=True, read_only=True)

    class Meta:
        model = Show
        fields = ('id', 'title', 'description', 'thumbnail', 'thumbnail_url', 'category_name', 'age_rating', 'teasers')

    def get_thumbnail_url(self, obj):
        try:
            return obj.thumbnail.url if obj.thumbnail else None
        except Exception:
            return None
