from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect, render

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from client.models import ClientProfile
from core.models import CustomUser, Register
from freelancer.models import FreelancerProfile

@login_required() 
def admin_view(request):
    if 'uid' not in request.session and not request.user.is_authenticated:
        return redirect('login_view')
    
    logged_user=request.user
    uid=request.user.id
    
    user=CustomUser.objects.get(id=uid)
    profile=Register.objects.get(user_id=uid)
    if user:
        return render(request, 'Admin/index.html',{'user1':user,'profile':profile})
    else:
        return redirect('login')


@login_required()
def user_list(request):
    if 'uid' not in request.session and not request.user.is_authenticated:
        return redirect('login_view')

    users = CustomUser.objects.all()
    clients = ClientProfile.objects.select_related('user')
    freelancers = FreelancerProfile.objects.select_related('user')
    registrations = Register.objects.select_related('user')  # Make sure to use select_related to avoid extra queries
    profile = Register.objects.get(user_id=request.user.id)

    context = {
        'users': users,
        'clients': clients,
        'freelancers': freelancers,
        'registrations': registrations,
        'profile': profile,
    }
    return render(request, 'Admin/UserView.html', context)




@login_required
def toggle_status(request, uid):
    user = CustomUser.objects.get(id=uid)
    if user.status == 'inactive':
        user.status = 'active'
    elif user.status == 'active':
        user.status = 'inactive'
    user.save()
    return redirect('administrator:user_list')  


@login_required
def toggle_permission(request, uid):
    user = CustomUser.objects.get(id=uid)
    if user.permission is False:
        user.permission = True
    elif user.permission is True:
        user.permission = False
    user.save()
    return redirect('administrator:user_list') 





@login_required
def account_settings(request):
    uid=request.user.id
    

    profile1 = CustomUser.objects.get(id=uid)
    profile=Register.objects.get(user_id=uid)
    
    return render(request, 'Admin/profile.html',{'profile1':profile1,'profile':profile})





@login_required
def change_password(request,uid):
    if 'uid' not in request.session:
        return redirect('login_view')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    if request.method=='POST':
        new_pass=request.POST.get('new_password')
        confirm_pass=request.POST.get('confirm_password')
        if new_pass==confirm_pass:
            profile1.set_password(new_pass)
            profile1.save()
            
            return redirect('administrator:account_settings')
    return render(request, 'Admin/profile.html',{'profile1':profile1,'profile2':profile2})  



@login_required
def change_profile_image(request,uid):
    if 'uid' not in request.session:
        return redirect('login_view')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    if request.method=='POST':
        
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            profile2.profile_picture = profile_picture
            profile2.save()
            
            return redirect('administrator:account_settings')
    return render(request, 'Admin/profile.html',{'profile1':profile1,'profile2':profile2})  
