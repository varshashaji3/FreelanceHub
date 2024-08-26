
from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username=models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    joined = models.DateTimeField(auto_now_add=True)

    ADMIN = 'admin'
    CLIENT = 'client'
    FREELANCER = 'freelancer'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (CLIENT, 'Client'),
        (FREELANCER, 'Freelancer'),
    ]

    role = models.CharField(max_length=20, blank=True, null=True, choices=ROLE_CHOICES, default='')
    welcome_email_sent = models.BooleanField(default=False)
    permission = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    google=models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  

    REQUIRED_FIELDS = []  
    def __str__(self):
        return self.email

  

    
class Register(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio_description = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.URLField(max_length=255, blank=True, null=True)
    instagram = models.URLField(max_length=255, blank=True, null=True)
    twitter = models.URLField(max_length=255, blank=True, null=True)
    
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    
    
    
class PasswordReset(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=50,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
  
  
class EmailVerification(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=50,default=None)
    created_at = models.DateTimeField(auto_now_add=True)  
    
    
    
class Event(models.Model):
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#ffffff')  # Hex color code
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='events')


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)