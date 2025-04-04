from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
import json
from .models import Project, ProjectMilestone

@login_required
def client_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('login')

    # Get all projects for the current user
    projects = Project.objects.filter(user=request.user)
    
    # Calculate key metrics
    total_projects = projects.count()
    active_projects = projects.filter(status='open').count()
    completed_projects = projects.filter(status='closed').count()
    recent_completed = projects.filter(
        status='closed',
        end_date__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Budget metrics
    total_budget = projects.aggregate(total=Sum('budget'))['total'] or 0
    spent_budget = projects.filter(status='closed').aggregate(total=Sum('budget'))['total'] or 0
    
    # Milestone metrics
    active_milestones = ProjectMilestone.objects.filter(
        project__user=request.user,
        status__in=['pending', 'in_progress']
    ).count()
    
    due_soon_milestones = ProjectMilestone.objects.filter(
        project__user=request.user,
        status__in=['pending', 'in_progress'],
        end_date__lte=timezone.now() + timedelta(days=7)
    ).count()
    
    # Project status distribution for chart
    status_counts = projects.values('status').annotate(count=Count('id'))
    project_status_data = [0, 0, 0, 0]  # [Open, In Progress, Completed, Closed]
    for status in status_counts:
        if status['status'] == 'open':
            project_status_data[0] = status['count']
        elif status['status'] == 'in_progress':
            project_status_data[1] = status['count']
        elif status['status'] == 'completed':
            project_status_data[2] = status['count']
        elif status['status'] == 'closed':
            project_status_data[3] = status['count']
    
    # Budget allocation by category
    category_budgets = projects.values('category').annotate(total=Sum('budget'))
    budget_categories = [item['category'] for item in category_budgets]
    budget_data = [float(item['total']) for item in category_budgets]
    
    # Recent activities
    recent_activities = []
    
    # Add project completions
    for project in projects.filter(status='closed').order_by('-end_date')[:5]:
        recent_activities.append({
            'date': project.end_date.strftime('%Y-%m-%d'),
            'title': f'Project Completed: {project.title}',
            'description': f'Budget: ₹{project.budget}'
        })
    
    # Add milestone completions
    for milestone in ProjectMilestone.objects.filter(
        project__user=request.user,
        status='completed'
    ).order_by('-updated_at')[:5]:
        recent_activities.append({
            'date': milestone.updated_at.strftime('%Y-%m-%d'),
            'title': f'Milestone Completed: {milestone.title}',
            'description': f'Project: {milestone.project.title}'
        })
    
    # Sort activities by date
    recent_activities.sort(key=lambda x: x['date'], reverse=True)
    recent_activities = recent_activities[:10]  # Keep only the 10 most recent
    
    # Upcoming milestones
    upcoming_milestones = ProjectMilestone.objects.filter(
        project__user=request.user,
        status__in=['pending', 'in_progress'],
        end_date__gte=timezone.now()
    ).order_by('end_date')[:5]
    
    context = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'recent_completed': recent_completed,
        'total_budget': total_budget,
        'spent_budget': spent_budget,
        'active_milestones': active_milestones,
        'due_soon_milestones': due_soon_milestones,
        'project_status_data': json.dumps(project_status_data),
        'budget_categories': json.dumps(budget_categories),
        'budget_data': json.dumps(budget_data),
        'recent_activities': recent_activities,
        'upcoming_milestones': upcoming_milestones,
    }
    
    return render(request, 'client/dashboard.html', context) 