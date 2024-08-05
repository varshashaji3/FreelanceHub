from django.shortcuts import redirect, render

from client.models import ClientProfile, Project
from core.decorators import nocache
from core.models import CustomUser, Register

from django.contrib.auth.decorators import login_required

from freelancer.models import FreelancerProfile, Proposal

@login_required
@nocache
def client_view(request):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role!='client':
        return redirect('login')

    uid = request.session['uid']
    logged_user=request.user
    uid=request.user.id
    
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    
    if logged_user.is_authenticated and profile2 and not any([
        profile2.phone_number or '',
        profile2.profile_picture or '',
        profile2.bio_description or '',
        profile2.location or ''
    ]):
        return render(request,'Client/Add_profile.html',{'profile2':profile2,'profile1':profile1,'uid':uid})
    return render(request,'Client/index.html',{'profile2':profile2,'profile1':profile1,'uid':uid})


@login_required
@nocache
def AddProfileClient(request, uid):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role!='client':
        return redirect('login')

    uid = request.session['uid']
    profile = Register.objects.get(user_id=uid)
    client_profile, created = ClientProfile.objects.get_or_create(user_id=uid)

    if request.method == 'POST':
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        phone_number = request.POST.get('phone_number')
        profile_picture = request.FILES.get('profile_picture')
        bio_description = request.POST.get('bio_description')
        location = request.POST.get('location')
        linkedin = request.POST.get('linkedin')
        instagram = request.POST.get('instagram')
        twitter = request.POST.get('twitter')
        client_type = request.POST.get('client_type')
        company_name = request.POST.get('company_name')
        industry = request.POST.get('industry')
        company_size = request.POST.get('company_size')
        website = request.POST.get('website')
        aadhar=request.FILES.get('aadhar')
        profile.first_name = first_name
        profile.last_name = last_name
        profile.phone_number = phone_number
        if profile_picture:
            profile.profile_picture = profile_picture
        profile.bio_description = bio_description
        profile.location = location
        profile.linkedin = linkedin
        profile.instagram = instagram
        profile.twitter = twitter
        profile.save()

        # Update ClientProfile
        client_profile.client_type = client_type
        if client_type == 'Company':
            client_profile.company_name = company_name
            client_profile.industry = industry
            client_profile.company_size = company_size
            client_profile.website = website
            client_profile.aadhaar_document=''
        else:
            client_profile.company_name = ''
            client_profile.industry = ''
            client_profile.company_size = ''
            client_profile.website = ''
            client_profile.aadhaar_document=aadhar
        client_profile.save()

        return redirect('client:client_view')

    return render(request, 'client/add_profile_client.html', {'profile': profile, 'client_profile': client_profile})


@login_required
@nocache
def account_settings(request):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role!='client':
        return redirect('login')
    uid=request.user.id
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    client=ClientProfile.objects.get(user_id=uid)
    
    return render(request, 'client/profile.html',{'profile1':profile1,'profile2':profile2,'client':client})


@login_required
@nocache
def change_password(request,uid):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role!='client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    client=ClientProfile.objects.get(user_id=uid)
    
    if request.method=='POST':
        new_pass=request.POST.get('new_password')
        confirm_pass=request.POST.get('confirm_password')
        if new_pass==confirm_pass:
            profile1.set_password(new_pass)
            profile1.save()
            
            return render(request, 'client/profile.html',{'profile1':profile1,'profile2':profile2,'client':client})
    return render(request, 'client/profile.html',{'profile1':profile1,'profile2':profile2,'client':client})
    
    
    
@login_required
@nocache   
def update_profile(request,uid):

    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role!='client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    client = ClientProfile.objects.get(user_id=uid)

    if request.method == 'POST':
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        phone_number = request.POST.get('phone_number')
        
        bio_description = request.POST.get('bio_description')
        location = request.POST.get('location')
        linkedin = request.POST.get('linkedin')
        instagram = request.POST.get('instagram')
        twitter = request.POST.get('twitter')
        company_name = request.POST.get('company_name')
        industry = request.POST.get('industry')
        company_size = request.POST.get('company_size')
        website = request.POST.get('website')
        aadhar=request.FILES.get('aadhar')
        profile2.first_name = first_name
        profile2.last_name = last_name
        profile2.phone_number = phone_number
        
        profile2.bio_description = bio_description
        profile2.location = location
        profile2.linkedin = linkedin
        profile2.instagram = instagram
        profile2.twitter = twitter
        profile2.save()

        client_type=client.client_type
        print(client_type)
        if client_type == 'Company':
            client.company_name = company_name
            client.industry = industry
            client.company_size = company_size
            client.website = website
            client.aadhaar_document=''
        else:
            client.company_name = ''
            client.industry = ''
            client.company_size = ''
            client.website = ''
            client.aadhaar_document=aadhar

        client.save()

        return redirect('client:account_settings')
    return render(request, 'client/profile.html',{'profile1':profile1,'profile2':profile2,'client':client})



@login_required
@nocache
def change_profile_image(request,uid):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role!='client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    client=ClientProfile.objects.get(user_id=uid)
    
    if request.method=='POST':
        
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            profile2.profile_picture = profile_picture
            profile2.save()
            
            return redirect('client:account_settings')
    return render(request, 'client/profile.html',{'profile1':profile1,'profile2':profile2,'client':client})


        
        
        
@login_required
@nocache
def freelancer_list(request):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role!='client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    client=ClientProfile.objects.get(user_id=uid)
    if profile1.permission:

        users_with_profiles = CustomUser.objects.filter(
            role='freelancer'
        ).select_related('freelancerprofile')
        
        registers = Register.objects.all()
        register_dict = {}
        for reg in registers:
            if reg.user_id not in register_dict:
                register_dict[reg.user_id] = []
            register_dict[reg.user_id].append(reg)
  
        
        context = []
        for user in users_with_profiles:
            user_data = {
                'user': user,
                'freelancer_profile': None,
                'registers': register_dict.get(user.id, [])
            }
            try:
                user_data['freelancer_profile'] = user.freelancerprofile
            except FreelancerProfile.DoesNotExist:
                pass
            context.append(user_data)

        return render(request, 'client/ViewFreelancers.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
            'users': context,
        })
    else:
        return render(request, 'client/PermissionDenied.html',{'profile1': profile1,
            'profile2': profile2,
            'client': client,})
        
        
        



      
@login_required
@nocache
def freelancer_detail(request, fid):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role!='client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    client=ClientProfile.objects.get(user_id=uid)
    if profile1.permission:
       
        profile3 = CustomUser.objects.get(id=fid)
        profile4=Register.objects.get(user_id=fid)
        freelancer=FreelancerProfile.objects.get(user_id=fid)
        
        return render(request, 'client/SingleFreelancer.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
            'client':client,
            'profile3':profile3,
            'profile4':profile4,
        })
    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })
        
                
        

@login_required
@nocache
def calendar(request):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role!='client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    client=ClientProfile.objects.get(user_id=uid)
    if profile1.permission==True:
        return render(request, 'client/calendar.html',{'profile1':profile1,'profile2':profile2,'client':client})
    else:
        return render(request, 'client/PermissionDenied.html',{'profile1': profile1,
            'profile2': profile2,
            'client': client,})
        
        


@login_required
@nocache
def add_new_project(request):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role!='client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    client=ClientProfile.objects.get(user_id=uid)
    categories = [
    "Web Development","Front-End Development","Back-End Development","Full-Stack Development","Mobile Development",
    "Android Development","iOS Development","UI/UX Design",
    "Graphic Design","Logo Design","Poster Design","Software Development",
    "Machine Learning Engineering","Artificial Intelligence"
]
    if profile1.permission==True:
        if request.method=='POST':
            title = request.POST.get('title')
            description = request.POST.get('description')
            budget = request.POST.get('budget')
            category = request.POST.get('category')
            allow_bid = 'allow_bid' in request.POST
            end_date = request.POST.get('end_date')
            file_upload = request.FILES.get('file')
            
            project = Project(
                title=title,
                description=description,
                budget=budget,
                category=category,
                allow_bid=allow_bid,
                end_date=end_date,
                file_upload=file_upload,
                user=request.user  
            )
            
            project.save()
            return redirect('client:project_list')
        return render(request, 'client/NewProject.html',{'profile1':profile1,'profile2':profile2,'client':client,'categories':categories})
    else:
        return render(request, 'client/PermissionDenied.html',{'profile1': profile1,
            'profile2': profile2,
            'client': client,})
        
        
        

@login_required
@nocache
def project_list(request):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role!='client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    client=ClientProfile.objects.get(user_id=uid)
    if profile1.permission==True:
        projects=Project.objects.filter(user_id=uid)
        return render(request, 'client/ProjectList.html',{'profile1':profile1,'profile2':profile2,'client':client,'projects':projects})
    else:
        return render(request, 'client/PermissionDenied.html',{'profile1': profile1,
            'profile2': profile2,
            'client': client,})      
        
        
        
        


@login_required
@nocache
def single_project_view(request,pid):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role!='client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    client=ClientProfile.objects.get(user_id=uid)
    if profile1.permission==True:
        project=Project.objects.get(id=pid)
        proposals = Proposal.objects.filter(project_id=pid).select_related('freelancer')
        freelancer_ids = proposals.values_list('freelancer__id', flat=True)
        reg_details = Register.objects.filter(user_id__in=freelancer_ids)
        freelancer_profiles = FreelancerProfile.objects.filter(user_id__in=freelancer_ids)
        
        for profile in freelancer_profiles:
            profile.skills = profile.skills.strip('[]').replace("'", "").split(', ') 
             
        return render(request, 'client/SingleProject.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
            'project': project,
            'proposals': proposals,
            'reg_details': reg_details,
            'freelancer_profiles': freelancer_profiles,
        })
        
    else:
        return render(request, 'client/PermissionDenied.html',{'profile1': profile1,
            'profile2': profile2,
            'client': client,})      
        
        
@login_required
def update_proposal_status(request, pro_id):
    proposal = Proposal.objects.get(id=pro_id)
    if request.method == 'POST':
        val = request.POST.get('status')
        if val in ['Pending', 'Accepted', 'Rejected']:
            proposal.status = val
            proposal.save()
    return redirect('client:project_list')