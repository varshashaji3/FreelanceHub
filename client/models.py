
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
    
    PROGRESS_CHOICES = (
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
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
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    project_status = models.CharField(max_length=50, default='Not Started')
    freelancer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='freelancer_projects')




class Repository(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='repositories')
    name = models.CharField(max_length=255, default='Default Repository')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f'Repository for {self.project.name}'


class SharedFile(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='shared_files')
    file = models.FileField(upload_to='shared_files/')
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class SharedURL(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='shared_urls')
    url = models.URLField(max_length=200)
    description = models.TextField(blank=True, null=True)
    shared_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    shared_at = models.DateTimeField(auto_now_add=True)

class SharedNote(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='shared_notes')
    note = models.TextField()
    added_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    

class Task(models.Model):
    PROJECT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    progress_percentage = models.FloatField(default=0.0)
    
    def save(self, *args, **kwargs):
        if self.start_date and self.start_date == timezone.now().date():
            self.status = 'In Progress'
        super().save(*args, **kwargs)
        
        
        


class FreelanceContract(models.Model):
    client = models.ForeignKey(CustomUser, related_name='client_contracts', on_delete=models.CASCADE)
    freelancer = models.ForeignKey(CustomUser, related_name='freelancer_contracts', on_delete=models.CASCADE)

    project = models.OneToOneField(Project, related_name='contract', on_delete=models.CASCADE)

    client_signature = models.ImageField(upload_to='signatures/client/', null=True, blank=True)
    freelancer_signature = models.ImageField(upload_to='signatures/freelancer/', null=True, blank=True)
    contract_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Contract {self.id} for Project {self.project_id}'
    

class PaymentInstallment(models.Model):
    contract = models.ForeignKey(FreelanceContract, related_name='installments', on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ], default='pending')
    
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'Installment {self.id} for Contract {self.contract.id}'