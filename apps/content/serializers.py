from rest_framework import serializers
from .models import Category, Author, Show, Episode, EpisodeAnalytics, Teaser

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
            'thumbnail': {'allow_null': True},
        }

class EpisodeSerializer(serializers.ModelSerializer):
    audio_file = serializers.FileField(write_only=True, required=False)
    audio_url = serializers.SerializerMethodField()

    class Meta:
        model = Episode
        fields = ('id', 'show', 'title', 'description', 'duration_seconds', 'sequence_number', 'audio_file_key', 'hls_playlist_key', 'audio_file', 'audio_url', 'created_at')
        extra_kwargs = {
            'audio_file_key': {'required': False},
            'hls_playlist_key': {'required': False},
        }

    def get_audio_url(self, obj):
        from services.storage import storage_service
        if obj.audio_file_key:
            try:
                return storage_service.generate_signed_url(obj.audio_file_key)
            except Exception:
                return None
        return None

    def create(self, validated_data):
        audio_file = validated_data.pop('audio_file', None)
        if audio_file:
            from django.core.files.storage import default_storage
            import uuid, os
            ext = os.path.splitext(audio_file.name)[1].lower()
            key = f"uploads/audio/{uuid.uuid4().hex}{ext}"
            default_storage.save(key, audio_file)
            validated_data['audio_file_key'] = key
        return super().create(validated_data)

    def update(self, instance, validated_data):
        audio_file = validated_data.pop('audio_file', None)
        if audio_file:
            from django.core.files.storage import default_storage
            import uuid, os
            # Delete old audio from R2 if exists
            if instance.audio_file_key:
                try:
                    default_storage.delete(instance.audio_file_key)
                except Exception:
                    pass
            ext = os.path.splitext(audio_file.name)[1].lower()
            key = f"uploads/audio/{uuid.uuid4().hex}{ext}"
            default_storage.save(key, audio_file)
            validated_data['audio_file_key'] = key
        return super().update(instance, validated_data)

class EpisodeDetailSerializer(EpisodeSerializer):
    pass

class EpisodeAnalyticsSerializer(serializers.ModelSerializer):
    plays = serializers.IntegerField(source='total_plays', read_only=True)
    avg_listen_time = serializers.SerializerMethodField()

    class Meta:
        model = EpisodeAnalytics
        fields = ('plays', 'avg_listen_time', 'completion_rate', 'likes', 'shares')

    def get_avg_listen_time(self, obj):
        minutes = int(obj.avg_listen_time)
        seconds = int((obj.avg_listen_time - minutes) * 60)
        return f"{minutes}:{seconds:02d}"

class TeaserSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    converted_show_title = serializers.ReadOnlyField(source='converted_show.title', default=None)

    class Meta:
        model = Teaser
        fields = ('id', 'title', 'image', 'image_url', 'sequence', 'is_active', 'is_converted', 'converted_show', 'converted_show_title', 'created_at')

    def get_image_url(self, obj):
        try:
            return obj.image.url if obj.image else None
        except Exception:
            return None

class PreloadEpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = ('id', 'title', 'sequence_number', 'duration_seconds', 'audio_file_key', 'hls_playlist_key')

class PreloadShowSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Show
        fields = ('id', 'title', 'description', 'thumbnail', 'thumbnail_url', 'category_name', 'age_rating')

    def get_thumbnail_url(self, obj):
        try:
            return obj.thumbnail.url if obj.thumbnail else None
        except Exception:
            return None
