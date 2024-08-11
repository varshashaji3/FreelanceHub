

from django.contrib import messages
from django.shortcuts import redirect, render

from client.models import ClientProfile, Project
from core.decorators import nocache
from core.models import CustomUser, Event, Notification, Register

from django.contrib.auth.decorators import login_required

from freelancer.models import FreelancerProfile, Proposal, ProposalFile
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

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
    notifications = Notification.objects.filter(user=request.user)
    events=Event.objects.filter(user=request.user)
    if logged_user.is_authenticated and profile2 and not any([
        profile2.phone_number or '',
        profile2.profile_picture or '',
        profile2.bio_description or '',
        profile2.location or ''
    ]):
        return render(request,'Client/Add_profile.html',{'profile2':profile2,'profile1':profile1,'uid':uid,'notifications':notifications,'events':events})
    return render(request,'Client/index.html',{'profile2':profile2,'profile1':profile1,'uid':uid,'notifications':notifications,'events':events})




@login_required
@nocache
def notification_mark_as_read(request,not_id):
    notification = Notification.objects.get(id=not_id)
    notification.is_read = True
    notification.save()
    next_url = request.GET.get('next', 'client:client_view')
    return redirect(next_url)


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
def change_password(request, uid):
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    client=ClientProfile.objects.get(user_id=uid)

    if request.method == 'POST':
        current = request.POST.get('current_password')
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')

        
        if profile1.check_password(current):
            profile1.set_password(new_pass)
            profile1.save()
            messages.success(request, 'Your password has been changed successfully!')
            return render(request, 'client/profile.html',{'profile1':profile1,'profile2':profile2,'client':client})
    
            
        else:
            messages.error(request, 'Current password is incorrect.')

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
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('login')

    uid = request.session.get('uid', request.user.id)
    profile1 = get_object_or_404(CustomUser, id=uid)
    profile2 = get_object_or_404(Register, user_id=uid)
    client = get_object_or_404(ClientProfile, user_id=uid)

    if profile1.permission:
        search_query = request.GET.get('search', '')
        profession_filter = request.GET.get('profession', '')
        skill_filter = request.GET.get('skill', '')

        users_with_profiles = CustomUser.objects.filter(
            role='freelancer',
            freelancerprofile__professional_title__isnull=False
        ).exclude(
            freelancerprofile__professional_title__exact=''
        ).select_related('freelancerprofile')

        if search_query:
            users_with_profiles = users_with_profiles.filter(
                Q(username__icontains=search_query) |
                Q(freelancerprofile__professional_title__icontains=search_query)
            )

        if profession_filter:
            users_with_profiles = users_with_profiles.filter(
                freelancerprofile__professional_title__icontains=profession_filter
            )

        if skill_filter:
            users_with_profiles = users_with_profiles.filter(
                freelancerprofile__skills__icontains=skill_filter
            )

        registers = Register.objects.all()
        register_dict = {}
        for reg in registers:
            register_dict.setdefault(reg.user_id, []).append(reg)

        context = []
        for user in users_with_profiles:
            freelancer_profile = getattr(user, 'freelancerprofile', None)
            professions = freelancer_profile.professional_title.strip('[]').replace("'", "").split(', ') if freelancer_profile and freelancer_profile.professional_title else []
            skills = freelancer_profile.skills.strip('[]').replace("'", "").split(', ') if freelancer_profile and freelancer_profile.skills else []

            context.append({
                'user': user,
                'freelancer_profile': freelancer_profile,
                'registers': register_dict.get(user.id, []),
                'professions': [title.strip() for title in professions],
                'skills': [skill.strip() for skill in skills]
            })

        profession_choices = [
            'Web Developer', 'Front-End Developer', 'Back-End Developer', 'Full-Stack Developer',
            'Mobile App Developer', 'Android Developer', 'iOS Developer', 'UI/UX Designer', 'Graphic Designer',
            'Logo Designer', 'Poster Designer', 'Machine Learning Engineer', 'Artificial Intelligence Specialist', 'Software Developer'
        ]

        skill_choices = [
            "java", "c++", "python", "eclipse", "visual studio", "html/css", "javascript", "bootstrap", "sass",
            "swift", "xcode", "kotlin", "android studio", "flutter", "react native", "r", "jupyter", "pandas",
            "numpy", "tensorflow", "pytorch", "keras", "scikit-learn", "adobe xd", "sketch", "figma", "invision",
            "react", "angular", "vue.js", "webpack", "node.js", "django", "ruby on rails", "spring boot",
            "mongodb", "express.js", "php (lamp stack)", "angular (mean stack)", "adobe illustrator",
            "coreldraw", "affinity designer", "adobe photoshop", "adobe indesign", "canva", "opencv"
        ]

        return render(request, 'client/ViewFreelancers.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
            'users': context,
            'search_query': search_query,
            'profession_filter': profession_filter,
            'skill_filter': skill_filter,
            'profession_choices': profession_choices,
            'skill_choices': skill_choices,
        })
    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })
        
        
        



      
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
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role != 'client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    client = ClientProfile.objects.get(user_id=uid)
    events = Event.objects.filter(user=uid)
    events_data = [
        {
            'id': event.id,  # Change this to 'id'
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
            'description': event.description,
            'color': event.color,
        }
        for event in events
    ]

    if profile1.permission:
        return render(request, 'client/calendar.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
            'events_data': events_data  
        })
    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })

        

 
 
 
 
@login_required
@nocache
def add_event(request):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role!='client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    client=ClientProfile.objects.get(user_id=uid)
    if profile1.permission==True:
        if request.method == 'POST':
            title = request.POST.get('title')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            description = request.POST.get('description')
            color = request.POST.get('color')
            
            user=request.user
            Event.objects.create(
                title=title,
                start_time=start_time,
                end_time=end_time,
                description=description,
                color=color,
                user=user
            )
            return redirect('client:calendar')
    else:
        return render(request, 'client/PermissionDenied.html',{'profile1': profile1,
            'profile2': profile2,
            'client': client,})   
        
@login_required
@nocache
def update_event(request):
    # Check user session and authentication
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('login')

    uid = request.session.get('uid')
    profile1 = get_object_or_404(CustomUser, id=uid)
    profile2 = get_object_or_404(Register, user_id=uid)
    client = get_object_or_404(ClientProfile, user_id=uid)

    if profile1.permission:
        if request.method == 'POST':
            event_id = request.POST.get('event_id')
            if not event_id:
                # Handle missing event_id case
                return redirect('client:calendar')  # or return an error message

            event = get_object_or_404(Event, id=event_id)

            title = request.POST.get('title')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            description = request.POST.get('description')
            color = request.POST.get('color')

            # Update event details
            event.title = title
            event.start_time = start_time
            event.end_time = end_time
            event.description = description
            event.color = color
            
            event.save()

            return redirect('client:calendar')

        elif request.method == 'GET':
            event_id = request.GET.get('event_id')
            if not event_id:
                # Handle missing event_id case
                return redirect('client:calendar')  # or return an error message

            event = get_object_or_404(Event, id=event_id)

            return render(request, 'client/edit_event.html', {
                'event': event,
                'profile1': profile1,
                'profile2': profile2,
                'client': client,
            })

    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })



@login_required
@nocache
def delete_event(request):
    if 'uid' not in request.session or not request.user.is_authenticated or request.user.role != 'client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = get_object_or_404(CustomUser, id=uid)
    profile2 = get_object_or_404(Register, user_id=uid)
    client = get_object_or_404(ClientProfile, user_id=uid)

    if profile1.permission:
        if request.method == 'POST':
            event_id = request.POST.get('event_id')
            if not event_id:
                return redirect('client:calendar')  # Handle missing event_id case

            try:
                event = Event.objects.get(id=event_id)
                event.delete()
            except Event.DoesNotExist:
                pass  # Handle case where event does not exist

            return redirect('client:calendar')

        else:
            return redirect('client:calendar')

    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })


@login_required
@nocache
def add_new_project(request):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role != 'client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    client = ClientProfile.objects.get(user_id=uid)
    
    categories = [
        "Web Development", "Front-End Development", "Back-End Development", "Full-Stack Development", "Mobile Development",
        "Android Development", "iOS Development", "UI/UX Design",
        "Graphic Design", "Logo Design", "Poster Design", "Software Development",
        "Machine Learning Engineering", "Artificial Intelligence"
    ]
    
    if profile1.permission:
        if request.method == 'POST':
            title = request.POST.get('title')
            description = request.POST.get('description')
            budget = request.POST.get('budget')
            category = request.POST.get('category')
            allow_bid = 'allow_bid' in request.POST
            end_date = request.POST.get('end_date')
            file_upload = request.FILES.get('file')
            
            # Check if a project with the same title already exists for this user
            if Project.objects.filter(title=title, user=request.user).exists():
                messages.error(request, 'A project with this title already exists!')
                return render(request, 'client/NewProject.html', {
                    'profile1': profile1, 
                    'profile2': profile2, 
                    'client': client, 
                    'categories': categories
                })
            
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
            projects = Project.objects.filter(user_id=uid)
            messages.success(request, 'New Project Added Successfully!!')
            return render(request, 'client/ProjectList.html', {
                'profile1': profile1,
                'profile2': profile2,
                'client': client,
                'projects': projects
            })
        return render(request, 'client/NewProject.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
            'categories': categories
        })
    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })

        

        
@login_required
@nocache
def edit_project(request, pid):
    if request.user.role != 'client':
        return redirect('login')

    uid = request.user.id
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    client = ClientProfile.objects.get(user_id=uid)
    categories = [
        "Web Development", "Front-End Development", "Back-End Development", "Full-Stack Development", "Mobile Development",
        "Android Development", "iOS Development", "UI/UX Design",
        "Graphic Design", "Logo Design", "Poster Design", "Software Development",
        "Machine Learning Engineering", "Artificial Intelligence"
    ]

    try:
        project = Project.objects.get(id=pid, user_id=uid)
    except Project.DoesNotExist:
        return redirect('client:project_list')

    if profile1.permission:
        if request.method == 'POST':
            title = request.POST.get('title')
            description = request.POST.get('description')
            budget = request.POST.get('budget')
            category = request.POST.get('category')
            allow_bid = 'allow_bid' in request.POST
            end_date = request.POST.get('end_date')
            file_upload = request.FILES.get('file')

            project.title = title
            project.description = description
            project.budget = budget
            project.category = category
            project.allow_bid = allow_bid
            project.end_date = end_date
            project.file_upload = file_upload

            project.save()
            return redirect('client:project_list')

        return render(request, 'client/UpdateProject.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
            'categories': categories,
            'project': project
        })
    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client
        })

        

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
    if profile1.permission:
        project = get_object_or_404(Project, id=pid)
        proposals = Proposal.objects.filter(project_id=project)
        
        freelancer_ids = proposals.values_list('freelancer__id', flat=True)
        reg_details = Register.objects.filter(user_id__in=freelancer_ids)
        freelancer_profiles = FreelancerProfile.objects.filter(user_id__in=freelancer_ids)
        
        for profile in freelancer_profiles:
            profile.skills = profile.skills.strip('[]').replace("'", "").split(', ')
        
        additional_files = ProposalFile.objects.filter(proposal__in=proposals)

        return render(request, 'client/SingleProject.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
            'project': project,
            'proposals': proposals,
            'reg_details': reg_details,
            'freelancer_profiles': freelancer_profiles,
            'additional_files': additional_files,
        })
        
    else:
        return render(request, 'client/PermissionDenied.html',{'profile1': profile1,
            'profile2': profile2,
            'client': client,})      
        
        
@login_required
@nocache
def toggle_project_status(request, pid):
    project = Project.objects.get(id=pid)
    if project.status == 'closed':
        project.status = 'open'
    elif project.status == 'open':
        project.status = 'closed'
    project.save()
    return redirect('client:project_list')         
        
        
@login_required
@nocache
def update_proposal_status(request, pro_id):
    proposal = Proposal.objects.get(id=pro_id)
    project = proposal.project
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        if new_status in ['Pending', 'Accepted', 'Rejected']:
            
            proposal.status = new_status
            proposal.save()

            
            if new_status == 'Accepted':
               
                Notification.objects.create(
                    user=proposal.freelancer,
                    message=f'Congratulations! Your proposal for project "{project.title}" has been accepted.'
                )
                
                Proposal.objects.filter(project=project).exclude(id=pro_id).update(status='Rejected')
                rejected_proposals = Proposal.objects.filter(project=project, status='Rejected')
                for other_proposal in rejected_proposals:
                    Notification.objects.create(
                        user=other_proposal.freelancer,
                        message=f'Your proposal for project "{project.title}" has been rejected.'
                    )
                
                messages.success(request, 'Yeyy.. you selected a Freelancer for this project.')
            else:
                Proposal.objects.filter(project=project).exclude(id=pro_id).update(status='Rejected')
                for other_proposal in Proposal.objects.filter(project=project, status='Rejected'):
                    Notification.objects.create(
                        user=other_proposal.freelancer,
                        message=f'Your proposal for project "{project.title}" has been rejected.'
                    )

    return redirect('client:single_project_view', pid=project.id)


@login_required
@nocache
def lock_proposal(request,prop_id):
    proposal = Proposal.objects.get(id=prop_id)
    proposal.locked = True
    proposal.save()
    return redirect('client:project_list')


     
@login_required
@nocache
def acc_deactivate(request):
    uid = request.user.id
    
    if uid is None:
        return redirect('login')
    user=CustomUser.objects.get(id=uid)
    user.status='inactive'
    user.save()
    subject = 'Account Deactivation Notice'
    
    client_profile = ClientProfile.objects.get(user_id=uid)
    if client_profile.client_type == 'Individual':
        
        register_info = Register.objects.get(user_id=uid)
        first_name = register_info.first_name
        last_name = register_info.last_name
        name = f"{first_name} {last_name}"
    else:  
        
        company_name = client_profile.company_name
        name = company_name
    context = {
        'user_name': name
    }
    html_content = render_to_string('client/deactivation.html', context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()
    return redirect('login')
