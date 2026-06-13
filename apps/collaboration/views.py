from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import StorySubmission, SponsorshipRequest
from .serializers import StorySubmissionSerializer, SponsorshipRequestSerializer

class StorySubmitView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StorySubmissionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserStoryListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StorySubmissionSerializer

    def get_queryset(self):
        return StorySubmission.objects.filter(user=self.request.user)

class SponsorshipSubmitView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SponsorshipRequestSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserSponsorshipListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SponsorshipRequestSerializer

    def get_queryset(self):
        return SponsorshipRequest.objects.filter(user=self.request.user)
