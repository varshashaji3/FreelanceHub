from client.models import Repository
from core.models import Notification
from client.models import Project

def unread_notifications(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
    else:
        unread_notifications = []
    return {'unread_notifications': unread_notifications}


def repository_list(request):
    if request.user.is_authenticated:
        assigned_projects = Project.objects.filter(freelancer=request.user)
        
        client_projects = Project.objects.filter(user=request.user)
        
        repositories = Repository.objects.filter(
            project__in=assigned_projects | client_projects
        ).distinct()
    else:
        repositories = []
    return {'repositories': repositories}

