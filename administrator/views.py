from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect, render

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from client.models import ClientProfile
from core.decorators import nocache
from core.models import CustomUser, Notification, Register
from freelancer.models import FreelancerProfile

from django.contrib import messages

from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from client.models import Project

@login_required
@nocache
def admin_view(request):
    if 'uid' not in request.session and not request.user.is_authenticated:
        return redirect('login_view')
    
    uid = request.user.id
    user = CustomUser.objects.get(id=uid)
    profile = Register.objects.get(user_id=uid)

    client_count = CustomUser.objects.filter(role='client').count()
    freelancer_count = CustomUser.objects.filter(role='freelancer').count()

    # Aggregate monthly user counts
    monthly_data = CustomUser.objects.annotate(month=TruncMonth('joined')).values('month').annotate(count=Count('id')).order_by('month')

    months = []
    client_counts = []
    freelancer_counts = []

    for month in monthly_data:
        month_name = month['month'].strftime('%b %Y')
        months.append(month_name)
        client_counts.append(CustomUser.objects.filter(role='client', joined__month=month['month'].month, joined__year=month['month'].year).count())
        freelancer_counts.append(CustomUser.objects.filter(role='freelancer', joined__month=month['month'].month, joined__year=month['month'].year).count())

    posted_count = Project.objects.all().count()
    completed_count = Project.objects.filter(project_status='Completed').count()
    in_progress_count = Project.objects.filter(project_status='In Progress').count()

    return render(request, 'Admin/index.html', {
        'user1': user,
        'profile': profile,
        'months': months,
        'client_counts': client_counts,
        'freelancer_counts': freelancer_counts,
        # Add project statistics to context
        'posted_count': posted_count,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
    })


@login_required
@nocache
def user_list(request):
    if not request.user.is_authenticated:
        return redirect('login_view')

    
    users = CustomUser.objects.select_related('register').all()
    clients = ClientProfile.objects.select_related('user')
    freelancers = FreelancerProfile.objects.select_related('user')
    
    
    profile = Register.objects.get(user_id=request.user.id)
    
    user_details = [{
        'first_name': user.register.first_name,
        'last_name': user.register.last_name
    } for user in users]
    
    context = {
        'users': users,
        'clients': clients,
        'freelancers': freelancers,
        'profile': profile,
        'user_details': user_details
    }
    
    return render(request, 'Admin/UserView.html', context)



@login_required
@nocache
def toggle_status(request, uid):
    user = CustomUser.objects.get(id=uid)
    
    if user.status == 'inactive':
        user.status = 'active'
        send_activation_email(uid)
    elif user.status == 'active':
        user.status = 'inactive'
        send_deactivation_email(uid)
    
    user.save()
    messages.success(request, 'User Status updated Successfully!!')
    return redirect('administrator:user_list')





@login_required
@nocache
def toggle_permission(request, uid):
    user = CustomUser.objects.get(id=uid)
    if user.permission is False:
        user.permission = True
        send_permission_email(uid)
        Notification.objects.create(
            user=user,
            message="Your permission has been granted."
        )
    elif user.permission is True:
        user.permission = False
        send_permission_denied_email(uid)
        Notification.objects.create(
            user=user,
            message="Your permission has been denied."
        )
    user.save()
    
    messages.success(request, 'User permission updated Successfully!!')
    return redirect('administrator:user_list') 






@login_required
@nocache
def account_settings(request):
    uid=request.user.id
    
    profile1 = CustomUser.objects.get(id=uid)
    profile=Register.objects.get(user_id=uid)
    
    return render(request, 'Admin/profile.html',{'profile1':profile1,'profile':profile})



@login_required
@nocache
def change_password(request, uid):
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)

    if request.method == 'POST':
        current = request.POST.get('current_password')
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')

        
        if profile1.check_password(current):
            profile1.set_password(new_pass)
            profile1.save()
            
            messages.success(request, 'Your password has been changed successfully!!')
            return redirect('administrator:account_settings')
    
            
        else:
            
            messages.error(request, 'Current password is incorrect!!')
            return redirect('administrator:account_settings')
    

    return render(request, 'Admin/profile.html',{'profile1':profile1,'profile2':profile2})  
    



@login_required
@nocache
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
            messages.success(request,'Your profile picture has been changed successfully!!')
            return redirect('administrator:account_settings')
    return render(request, 'Admin/profile.html',{'profile1':profile1,'profile2':profile2})  


















# MAILS




def send_permission_email(uid):
    user = CustomUser.objects.get(id=uid)
    print(uid)
    subject = 'Access Granted: Welcome to FreelanceHub!'
    
    if user.role == 'client':
        client_profile = ClientProfile.objects.get(user_id=uid)
        if client_profile.client_type == 'Individual':
            
            register_info = Register.objects.get(user_id=uid)
            first_name = register_info.first_name
            last_name = register_info.last_name
            name = f"{first_name} {last_name}"
        else:  
            
            company_name = client_profile.company_name
            name = company_name
    else:  
        
        register_info = Register.objects.get(user=uid)
        first_name = register_info.first_name
        last_name = register_info.last_name
        name = f"{first_name} {last_name}"
    
    context = {
        'user_name': name
    }
    html_content = render_to_string('Admin/permission_done.html', context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()






def send_permission_denied_email(uid):
    user = CustomUser.objects.get(id=uid)
    subject = 'Permission Denied'
    
    if user.role == 'client':
        client_profile = ClientProfile.objects.get(user_id=uid)
        if client_profile.client_type == 'Individual':
            
            register_info = Register.objects.get(user_id=uid)
            first_name = register_info.first_name
            last_name = register_info.last_name
            name = f"{first_name} {last_name}"
        else:  
            
            company_name = client_profile.company_name
            name = company_name
    else:  
        
        register_info = Register.objects.get(user_id=uid)
        first_name = register_info.first_name
        last_name = register_info.last_name
        name = f"{first_name} {last_name}"
    
    
    context = {
        'user_name': name
    }
    html_content = render_to_string('Admin/permission_denied.html', context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()
    
    
    
    
    

def send_deactivation_email(uid):
    subject = 'Account Deactivation Notice'
    user = CustomUser.objects.get(id=uid)
    if user.role == 'client':
        client_profile = ClientProfile.objects.get(user_id=uid)
        if client_profile.client_type == 'Individual':
            
            register_info = Register.objects.get(user_id=uid)
            first_name = register_info.first_name
            last_name = register_info.last_name
            name = f"{first_name} {last_name}"
        else:  
            
            company_name = client_profile.company_name
            name = company_name
    else:  
        
        register_info = Register.objects.get(user_id=uid)
        first_name = register_info.first_name
        last_name = register_info.last_name
        name = f"{first_name} {last_name}"
    
    context = {
        'user_name': name
    }
    html_content = render_to_string('Admin/account_activated.html', context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()




def send_activation_email(uid):
    subject = 'Account Activation Notice'
    user = CustomUser.objects.get(id=uid)
    if user.role == 'client':
        client_profile = ClientProfile.objects.get(user_id=uid)
        if client_profile.client_type == 'Individual':
            
            register_info = Register.objects.get(user_id=uid)
            first_name = register_info.first_name
            last_name = register_info.last_name
            name = f"{first_name} {last_name}"
        else:  
            
            company_name = client_profile.company_name
            name = company_name
    else:  
        
        register_info = Register.objects.get(user_id=uid)
        first_name = register_info.first_name
        last_name = register_info.last_name
        name = f"{first_name} {last_name}"
    
    context = {
        'user_name': name
    }
    html_content = render_to_string('Admin/account_deactivated.html', context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()
