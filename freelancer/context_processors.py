from freelancer.models import FreelancerProfile
from core.models import CustomUser, Register
from django.shortcuts import get_object_or_404
from core.models import UserSubscription

def freelancer_context(request):
    if request.user.is_authenticated and request.user.role == 'freelancer':
        uid = request.user.id
        profile1 = get_object_or_404(CustomUser, id=uid)
        profile2 = get_object_or_404(Register, user_id=uid)
        
        try:
            freelancer = FreelancerProfile.objects.get(user_id=uid)
        except FreelancerProfile.DoesNotExist:
            freelancer = None  # or handle the case when it doesn't exist

        # Using related_name to get active subscription
        active_subscription = request.user.subscriptions.filter(
            is_active=True
        ).select_related('plan').first()

        return {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
            'active_subscription': active_subscription,
        }
    return {}
