from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

from django.conf import settings

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver

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
    complaint_count = models.PositiveIntegerField(default=0)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  

    REQUIRED_FIELDS = []  
    def __str__(self):
        return self.email

  

    
class Register(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio_description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.URLField(max_length=255, blank=True, null=True)
    instagram = models.URLField(max_length=255, blank=True, null=True)
    twitter = models.URLField(max_length=255, blank=True, null=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    
    
class PasswordReset(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=50, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)  # New field for expiration time

    def is_expired(self):
        return timezone.now() > self.expires_at  # Method to check if the token is expired


class EmailVerification(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=50, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)  # New field for expiration time

    def is_expired(self):
        return timezone.now() > self.expires_at  # Method to check if the token is expired
    
    
    
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
    
    

class SiteReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # The user who wrote the review
    review_text = models.TextField()  
    rating = models.PositiveIntegerField()  
    created_at = models.DateTimeField(default=timezone.now)  

    def __str__(self):
        return f"Review by {self.user} on {self.created_at}"

    def is_due_for_review(self, months=3):
        """
        Check if the review should be requested based on the given number of months.
        """
        threshold_date = self.created_at + relativedelta(months=months)
        return timezone.now() >= threshold_date
    
    
    
from client.models import Project,FreelanceContract
from django.conf import settings
from django.utils import timezone
class CancellationRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cancellation_requests_made')
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cancellation_requests_to_approve')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    requested_date = models.DateTimeField(default=timezone.now)
    response_date = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True, null=True) 
    def __str__(self):
        return f"Cancellation Request for Project {self.project.id} by {self.requested_by}"



class RefundPayment(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    pay_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_refund_payments')
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    compensation_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    project = models.ForeignKey('client.Project', on_delete=models.CASCADE, null=True, blank=True)  # New field

    def __str__(self):
        return f"Refund Payment of {self.amount} to {self.pay_to} for Project {self.project.id}"

class SubscriptionPlan(models.Model):
    # Basic Details
    name = models.CharField(
        max_length=100, 
        unique=True,
        null=False, 
        blank=False,
        help_text="Plan name (e.g., Basic, Premium, Pro)"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=False,
        blank=False,
        default=0.00,
        help_text="Price for the plan"
    )
    duration_days = models.IntegerField(
        null=False,
        blank=False,
        default=30,
        help_text="Duration of the plan in days"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the plan is currently active"
    )
    
    # Client Features
    can_hire_freelancer = models.BooleanField(
        default=False,
        help_text="Allow clients to hire freelancers"
    )
    can_create_events = models.BooleanField(
        default=False,
        help_text="Allow clients to create events"
    )
    project_creation_limit = models.IntegerField(
        default=0,
        null=False,
        blank=False,
        help_text="Maximum number of projects a client can create"
    )
    ai_freelancer_recommendations = models.BooleanField(
        default=False,
        help_text="Enable AI freelancer recommendations for clients"
    )
    
    # Freelancer Features
    # The code `can_participate_events` is not a valid Python code snippet. It seems to be a function
    # or variable name, but without the actual code implementation, it is not possible to determine
    # what it is doing. If you provide the code implementation, I can help explain its functionality.
    can_participate_events = models.BooleanField(
        default=False,
        help_text="Allow freelancers to participate in events"
    )
    ai_skill_gap_analysis = models.BooleanField(
        default=False,
        help_text="Enable AI skill gap analysis for freelancers"
    )
    can_create_portfolio = models.BooleanField(
        default=False,
        help_text="Allow freelancers to create portfolio"
    )
    max_proposals_limit = models.IntegerField(
        default=0,
        null=False,
        blank=False,
        help_text="Maximum number of proposals a freelancer can submit"
    )
    ai_project_recommendations = models.BooleanField(
        default=False,
        help_text="Enable AI project recommendations for freelancers"
    )
    team_creation = models.BooleanField(
        default=False,
        help_text="Allow freelancers to create teams"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the plan was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the plan was last updated"
    )

    class Meta:
        ordering = ['price', 'name']
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"

    def __str__(self):
        return f"{self.name} (${self.price})"

    @property
    def badge(self):
        """Returns the plan name as the badge"""
        return self.name

class UserSubscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True)
    
    # Payment Details
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(max_length=20, default='Pending')
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Subscription Dates
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the subscription ends"
    )
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan.name if self.plan else 'No Plan'}"

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.is_active:
            UserSubscription.objects.filter(
                user=self.user,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-start_date']

    @property
    def payment_completed(self):
        return self.payment_status == 'Completed'

    @property
    def is_expired(self):
        if self.end_date:
            return timezone.now() > self.end_date
        return False

    @property
    def days_remaining(self):
        if self.end_date:
            delta = self.end_date - timezone.now()
            return max(0, delta.days)
        return 0

    def set_subscription_period(self):
        """Set the subscription period based on the plan duration"""
        if self.plan and self.plan.duration_days:
            self.start_date = timezone.now()
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
            self.save()
            return True
        return False

    @property
    def check_expiry(self):
        """Check if subscription has expired"""
        if self.end_date and timezone.now() > self.end_date:
            self.is_active = False
            self.save()

# Signal to check expiry before any subscription is accessed
@receiver(pre_save, sender=UserSubscription)
def check_subscription_expiry(sender, instance, **kwargs):
    if instance.end_date and timezone.now() > instance.end_date:
        instance.is_active = False

def set_subscription_end_date(subscription):
    subscription.end_date = subscription.start_date + timedelta(days=subscription.plan.duration_days)
    subscription.save()
