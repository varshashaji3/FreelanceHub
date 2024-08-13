
from datetime import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import CustomUser

class ClientProfile(models.Model):
    CLIENT_TYPE_CHOICES = (
        ('Individual', 'Individual'),
        ('Company', 'Company'),
    )
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    client_type = models.CharField(max_length=50, choices=CLIENT_TYPE_CHOICES, default='Individual')
    company_name = models.CharField(max_length=255, null=True, blank=True)
    website = models.URLField(max_length=255, null=True, blank=True)
    license_number = models.CharField(max_length=255, null=True, blank=True)
    
    aadhaar_document = models.FileField(upload_to='aadhaar/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    

class Project(models.Model):
    STATUS_CHOICES = (
        ('open', 'open'),
        ('closed', 'closed'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.IntegerField()
    category = models.CharField(max_length=605)  
    allow_bid = models.BooleanField(default=False)
    end_date = models.DateField(null=True, blank=True)
    file_upload = models.FileField(upload_to='project_files/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='client_projects')  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    freelancer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='freelancer_projects')


