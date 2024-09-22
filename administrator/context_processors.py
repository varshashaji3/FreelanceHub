from core.models import CustomUser, Register

def user_profile(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(id=request.user.id)
        profile = Register.objects.get(user_id=request.user.id)
        return {
            'user': user,
            'profile': profile,
        }
    return {}
