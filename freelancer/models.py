
from django.db import models

from client.models import Project
from core.models import CustomUser  

    
from ckeditor.fields import RichTextField
from django.utils import timezone

class FreelancerProfile(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    professional_title = models.TextField(max_length=255)
    skills = models.TextField(max_length=255)
    experience_level = models.CharField(max_length=50, blank=True, null=True)
    portfolio_link = models.URLField(max_length=255, blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    aadhaar_document = models.FileField(upload_to='aadhaar/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    aadhaar_face_image = models.ImageField(upload_to='aadhaar/faces/', null=True, blank=True)  # Cropped face from Aadhar
    verification_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('verified', 'Verified'), ('failed', 'Failed')], default='pending')
    verification_attempts = models.IntegerField(default=0)

class Todo(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=50,default=None)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    

class Proposal(models.Model):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='proposals')
    
    freelancer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='proposals')

    date_issued = models.DateField(default=timezone.now)
    proposal_details = RichTextField()  
    budget = models.DecimalField(max_digits=10, decimal_places=2)  
    deadline = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    fancy_num=models.CharField(max_length=5, unique=True, blank=True)
    proposal_file = models.FileField(upload_to='proposals/', null=True, blank=True)
    locked = models.BooleanField(default=False)
    

    

class ProposalFile(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='proposal_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
