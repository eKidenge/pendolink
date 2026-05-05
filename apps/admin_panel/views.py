from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import timedelta
from apps.users.models import User
from apps.billing.models import UserSubscription, Transaction
from apps.matching.models import Like, Match
from apps.moderation.models import ReportedContent

@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # User statistics
    total_users = User.objects.count()
    new_users_today = User.objects.filter(date_joined__date=today).count()
    new_users_week = User.objects.filter(date_joined__date__gte=week_ago).count()
    active_users = User.objects.filter(last_active__date=today).count()
    
    # Premium statistics
    premium_users = User.objects.filter(is_premium=True).count()
    active_subscriptions = UserSubscription.objects.filter(
        is_active=True, 
        end_date__gte=timezone.now()
    ).count()
    
    # Revenue statistics
    total_revenue = Transaction.objects.filter(
        status='completed',
        created_at__date__gte=month_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Match statistics
    total_matches = Match.objects.filter(created_at__date__gte=month_ago).count()
    
    # Report statistics
    pending_reports = ReportedContent.objects.filter(status='pending').count()
    
    # Recent users
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # User growth data for chart - as lists, not strings
    user_growth_dates = []
    user_growth_data = []
    for i in range(7, -1, -1):
        date = today - timedelta(days=i)
        count = User.objects.filter(date_joined__date=date).count()
        user_growth_dates.append(date.strftime('%m/%d'))
        user_growth_data.append(count)
    
    # Revenue data for chart - as lists, not strings
    revenue_dates = []
    revenue_data = []
    for i in range(7, -1, -1):
        date = today - timedelta(days=i)
        revenue = Transaction.objects.filter(
            status='completed',
            created_at__date=date
            ).aggregate(total=Sum('amount'))['total'] or 0
        revenue_dates.append(date.strftime('%m/%d'))
        revenue_data.append(float(revenue))
    
    # Prepare data for recent users
    recent_users_data = []
    for user in recent_users:
        recent_users_data.append({
            'id': user.id,
            'username': user.username,
            'profile_picture': None,
            'location': user.location.town if hasattr(user, 'location') else 'Unknown',
            'joined_at': user.date_joined,
            'is_verified': user.is_verified
        })
    
    context = {
        'today': today,
        'total_users': total_users,
        'new_users_today': new_users_today,
        'new_users_week': new_users_week,
        'active_users': active_users,
        'active_percentage': round((active_users / total_users * 100) if total_users > 0 else 0, 1),
        'premium_users': premium_users,
        'active_subscriptions': active_subscriptions,
        'conversion_rate': round((premium_users / total_users * 100) if total_users > 0 else 0, 1),
        'revenue_mtd': int(total_revenue),
        'revenue_growth': 15,
        'total_matches': total_matches,
        'pending_reports': pending_reports,
        'api_response_time': 120,
        'active_sessions': active_users,
        'user_growth_dates': user_growth_dates,
        'user_growth_data': user_growth_data,
        'revenue_dates': revenue_dates,
        'revenue_data': revenue_data,
        'recent_users': recent_users_data,
        'pending_reports_data': [],  # Empty for now
    }
    return render(request, 'admin/dashboard.html', context)

@staff_member_required
def admin_users(request):
    """User management page"""
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin/users.html', {'users': users})

@staff_member_required
def admin_reports(request):
    """Reports management page"""
    reports = ReportedContent.objects.all().order_by('-created_at')
    return render(request, 'admin/reports.html', {'reports': reports})

@staff_member_required
def admin_analytics(request):
    """Analytics page"""
    return render(request, 'admin/analytics.html')