from rest_framework import serializers
from .models import StorySubmission, SponsorshipRequest

class StorySubmissionSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.phone_number')
    
    class Meta:
        model = StorySubmission
        fields = ('id', 'username', 'title', 'content', 'status', 'rejection_reason', 'created_at')
        read_only_fields = ('id', 'status', 'rejection_reason', 'created_at')

class SponsorshipRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SponsorshipRequest
        fields = ('id', 'brand_name', 'description', 'ad_visual', 'target_url', 'status', 'rejection_reason', 'created_at')
        read_only_fields = ('id', 'status', 'rejection_reason', 'created_at')
