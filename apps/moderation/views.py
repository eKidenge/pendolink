from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from django.utils import timezone
from datetime import timedelta
from .models import ReportedContent, UserFlag, ModerationAction
from .serializers import ReportedContentSerializer, UserFlagSerializer
from apps.permissions.permissions import IsAdminUser

class ReportListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReportedContentSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return ReportedContent.objects.all().order_by('-created_at')
        return ReportedContent.objects.filter(reported_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    queryset = ReportedContent.objects.all()
    serializer_class = ReportedContentSerializer

class ReportAssignView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def post(self, request, pk):
        try:
            report = ReportedContent.objects.get(id=pk)
            report.assigned_to = request.user
            report.status = 'investigating'
            report.save()
            return Response({'status': 'assigned'})
        except ReportedContent.DoesNotExist:
            return Response({'error': 'Report not found'}, status=404)

class ReportResolveView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def post(self, request, pk):
        try:
            report = ReportedContent.objects.get(id=pk)
            report.status = 'resolved'
            report.resolution_notes = request.data.get('notes', '')
            report.resolved_by = request.user
            report.resolved_at = timezone.now()
            report.save()
            return Response({'status': 'resolved'})
        except ReportedContent.DoesNotExist:
            return Response({'error': 'Report not found'}, status=404)

class FlagListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    queryset = UserFlag.objects.filter(is_active=True)
    serializer_class = UserFlagSerializer

class SuspiciousUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        flagged_users = UserFlag.objects.filter(is_active=True).values('user').distinct()
        return Response({'flagged_count': flagged_users.count()})

class ModerationQueueView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        pending = ReportedContent.objects.filter(status='pending').order_by('created_at')
        investigating = ReportedContent.objects.filter(status='investigating').order_by('-updated_at')
        
        return Response({
            'pending': ReportedContentSerializer(pending, many=True).data,
            'investigating': ReportedContentSerializer(investigating, many=True).data,
        })

class ModerationStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        stats = {
            'pending_count': ReportedContent.objects.filter(status='pending').count(),
            'investigating_count': ReportedContent.objects.filter(status='investigating').count(),
            'resolved_today': ReportedContent.objects.filter(
                resolved_at__date=timezone.now().date()
            ).count(),
        }
        return Response(stats)