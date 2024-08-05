from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

from client.models import ClientProfile, Project
from core.decorators import nocache
from core.models import CustomUser, Register

from django.contrib.auth.decorators import login_required

from freelancer.models import FreelancerProfile, Proposal, Todo

from django.contrib import messages

@login_required
@nocache
def freelancer_view(request):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role!='freelancer':
        return redirect('login')
        
    uid = request.session['uid']
    logged_user=request.user
    uid=request.user.id
    profile2=Register.objects.get(user_id=uid)
    todos = Todo.objects.filter(user_id=uid)
    profile1=CustomUser.objects.get(id=uid)
    if logged_user.is_authenticated and profile2 and not any([
        profile2.phone_number or '',
        profile2.profile_picture or '',
        profile2.bio_description or '',
        profile2.location or ''
    ]):
        return render(request,'freelancer/Add_profile.html',{'profile1':profile1,'profile2':profile2,'uid':uid,'todos':todos,})
    return render(request,'freelancer/index.html',{'profile2':profile2,'profile1':profile1,'uid':uid,'todos':todos,})


@login_required
@nocache
def AddProfileFreelancer(request, uid):
   

    if not request.user.is_authenticated:
        return redirect('login')

    user = CustomUser.objects.get(id=uid)
    profile, created = FreelancerProfile.objects.get_or_create(user=user)
    todos = Todo.objects.filter(user_id=uid)
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
        professional_titles = request.POST.getlist('professional_titles')
        experience_level = request.POST.get('experience_level')
        portfolio_link = request.POST.get('portfolio_link')
        education = request.POST.get('education')
        resume = request.FILES.get('resume')
        aadhaar = request.FILES.get('aadhaar')
        selected_skills = request.POST.getlist('skills')

        register, _ = Register.objects.get_or_create(user=user)
        register.first_name = first_name
        register.last_name = last_name
        register.phone_number = phone_number
        if profile_picture:
            register.profile_picture = profile_picture
        register.bio_description = bio_description
        register.location = location
        register.linkedin = linkedin
        register.instagram = instagram
        register.twitter = twitter
        register.save()

        # Update FreelancerProfile (freelancer-specific fields)
        profile.experience_level = experience_level
        profile.portfolio_link = portfolio_link
        profile.education = education
        if resume:
            profile.resume = resume
        if aadhaar:
            profile.aadhaar_document = aadhaar
        profile.skills=selected_skills
        
        profile.professional_title = professional_titles
        profile.save()

        return redirect('freelancer:freelancer_view')

    context = {
        'profile': profile,
        'uid': uid,
        'todos':todos,
    }

    return render(request, 'freelancer/Add_profile.html', context)




@login_required
@nocache
def account_settings(request):
    uid=request.user.id
    profession = [
    'Web Developer','Front-End Developer','Back-End Developer','Full-Stack Developer',
    'Mobile App Developer','Android Developer','iOS Developer','UI/UX Designer','Graphic Designer',
    'Logo Designer','Poster Designer','Machine Learning Engineer','Artificial Intelligence Specialist','Software Developer',
]
    skills = [
    "java", "c++", "python", "eclipse", "visual studio", "html/css", "javascript", "bootstrap", "sass", 
    "swift", "xcode", "kotlin", "android studio", "flutter", "react native", "r", "jupyter", "pandas", 
    "numpy", "tensorflow", "pytorch", "keras", "scikit-learn", "adobe xd", "sketch", "figma", "invision", 
    "react", "angular", "vue.js", "webpack", "node.js", "django", "ruby on rails", "spring boot", 
    "mongodb", "express.js", "php (lamp stack)", "angular (mean stack)", "adobe illustrator", 
    "coreldraw", "affinity designer", "adobe photoshop", "adobe indesign", "canva", "opencv"
]

    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    freelancer=FreelancerProfile.objects.get(user_id=uid)
    todos = Todo.objects.filter(user_id=uid)
    if freelancer.professional_title:
        freelancer.professional_title = freelancer.professional_title.strip('[]').replace("'", "").split(', ')
    else:
        freelancer.professional_title = []

    if freelancer.skills:
        freelancer.skills = freelancer.skills.strip('[]').replace("'", "").split(', ')
    else:
        freelancer.skills = []
    return render(request, 'freelancer/accounts.html',{'profile1':profile1,
                                                       'profile2':profile2,
                                                       
                                                       'freelancer':freelancer,
                                                       'profession':profession,
                                                       'skills':skills,'todos':todos,
                                                       
                                                       })





@login_required
@nocache
def change_password(request, uid):
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)
    todos = Todo.objects.filter(user_id=uid)

    if request.method == 'POST':
        current = request.POST.get('current_password')
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')

        
        if profile1.check_password(current):
            profile1.set_password(new_pass)
            profile1.save()
            messages.success(request, 'Your password has been changed successfully!')
            return render(request, 'freelancer/accounts.html', {
                'profile1': profile1,
                'profile2': profile2,
                'freelancer': freelancer,
                'todos': todos,
            })
            
        else:
            messages.error(request, 'Current password is incorrect.')

    return render(request, 'freelancer/accounts.html', {
        'profile1': profile1,
        'profile2': profile2,
        'freelancer': freelancer,
        'todos': todos,
    })


@login_required
@nocache
def update_profile(request,uid):
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)
    todos = Todo.objects.filter(user_id=uid)
    
    if request.method == 'POST':
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        phone_number = request.POST.get('phone_number')
        bio_description = request.POST.get('bio_description')
        location = request.POST.get('location')
        linkedin = request.POST.get('linkedin')
        instagram = request.POST.get('instagram')
        twitter = request.POST.get('twitter')
        professional_titles = request.POST.getlist('professional_titles')
        experience_level = request.POST.get('experience_level')
        portfolio_link = request.POST.get('portfolio_link')
        education = request.POST.get('education')
        resume = request.FILES.get('resume')
        aadhaar = request.FILES.get('aadhaar')
        selectedskills = request.POST.getlist('skills')
        profile2.first_name = first_name
        profile2.last_name = last_name
        profile2.phone_number = phone_number
        
        profile2.bio_description = bio_description
        profile2.location = location
        profile2.linkedin = linkedin
        profile2.instagram = instagram
        profile2.twitter = twitter
        profile2.save()

        freelancer.experience_level = experience_level
        freelancer.portfolio_link = portfolio_link
        freelancer.education = education
        if resume:
            freelancer.resume = resume
        if aadhaar:
            freelancer.aadhaar_document = aadhaar
        freelancer.skills=selectedskills
        
        freelancer.professional_title = professional_titles
        freelancer.save()

        return redirect('freelancer:account_settings')
    return render(request, 'freelancer/accounts.html',{'profile1':profile1,'profile2':profile2,'freelancer':freelancer,'todos':todos,})  
  
  

@login_required
@nocache
def change_profile_image(request,uid):
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    freelancer=FreelancerProfile.objects.get(user_id=uid)
    todos = Todo.objects.filter(user_id=uid)
    if request.method=='POST':
        
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            profile2.profile_picture = profile_picture
            profile2.save()
            
            return redirect('freelancer:account_settings')
    return render(request, 'freelancer/accounts.html',{'profile1':profile1,'profile2':profile2,'freelancer':freelancer,'todos':todos,})  


   
        
@login_required
@nocache
def client_list(request):
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    freelancer=FreelancerProfile.objects.get(user_id=uid)
    if profile1.permission:
        todos = Todo.objects.filter(user_id=uid)
        
        users_with_profiles = CustomUser.objects.filter(role='client').select_related('clientprofile')

        registers = Register.objects.all()
        register_dict = {reg.user_id: reg for reg in registers}  
        
        
        context = [
            {
                'user': user,
                'client_profile': user.clientprofile if hasattr(user, 'clientprofile') else None,
                'register': register_dict.get(user.id)  
            }
            for user in users_with_profiles
        ]

        return render(request, 'freelancer/ViewClients.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
            'users': context,
            'todos':todos,
        })
    else:
        return render(request, 'freelancer/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
        })
        
        
        
        
@login_required
@nocache
def client_detail(request, cid):
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    freelancer=FreelancerProfile.objects.get(user_id=uid)
    if profile1.permission:
       
        profile3 = CustomUser.objects.get(id=cid)
        profile4=Register.objects.get(user_id=cid)
        client=ClientProfile.objects.get(user_id=cid)
        todos = Todo.objects.filter(user_id=uid)
    
        return render(request, 'freelancer/SingleClient.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
            'profile3':profile3,
            'profile4':profile4,
            'client':client,
            'todos':todos,
        })
    else:
        return render(request, 'freelancer/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
        })
        
        
        
        
@login_required
@nocache
def calendar(request):
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    freelancer=FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission==True:
        todos = Todo.objects.filter(user_id=uid)
        return render(request, 'freelancer/calendar.html',{'profile1':profile1,'profile2':profile2,'freelancer':freelancer,'todos':todos})
    else:
        return render(request, 'freelancer/PermissionDenied.html',{'profile1':profile1,'profile2':profile2,'freelancer':freelancer})
        


@login_required
@nocache
def todo(request):
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    freelancer=FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission==True:
        todos = Todo.objects.filter(user_id=uid)
        return render(request, 'freelancer/todo.html',{'profile1':profile1,'profile2':profile2,'freelancer':freelancer,'todos':todos})
    else:
        return render(request, 'freelancer/PermissionDenied.html',{'profile1':profile1,'profile2':profile2,'freelancer':freelancer})
        


@login_required
@nocache
def add_todo(request,user_id):
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    freelancer=FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission==True:
        if request.method=='POST':
            title=request.POST.get('title')
            next_url = request.POST.get('next')
            Todo.objects.create(user=profile1,title=title)
            return redirect(next_url)
        todos = Todo.objects.filter(user_id=uid)
        return render(request, 'freelancer/todo.html',{'profile1':profile1,'profile2':profile2,'freelancer':freelancer,'todos':todos})
    else:
        return render(request, 'freelancer/PermissionDenied.html',{'profile1':profile1,'profile2':profile2,'freelancer':freelancer})
        
                            


@login_required
@nocache
def update_todo(request, todo_id):
    uid = request.session.get('uid')
    
    if uid is None:
        return redirect('login')

    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        

            
        return render(request, 'freelancer/update_todo.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
            'todo': todo
        })
    else:
        return render(request, 'freelancer/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer
        })




@login_required
@nocache
def delete_todo(request, todo_id):
    uid = request.session.get('uid')

    if uid is None:
        return redirect('login')

    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        if request.method == 'POST':
            Todo.objects.filter(id=todo_id).delete()
            return redirect(request.POST.get('next')) 
    else:
        return render(request, 'freelancer/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer
        })

    todos = Todo.objects.filter(user_id=uid)
    return render(request, 'freelancer/todo.html', {
        'profile1': profile1,
        'profile2': profile2,
        'freelancer': freelancer,
        'todos': todos
    })
        
        
        
               
        

@login_required
@nocache
def view_project(request):
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    freelancer=FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission==True:
        todos = Todo.objects.filter(user_id=uid)
        projects = Project.objects.all()

        project_details = []
        for project in projects:
            cid = project.user_id
            client_profile = ClientProfile.objects.get(user_id=cid)
            client_register = Register.objects.get(user_id=cid)
            project_details.append({
                'project': project,
                'client_profile': client_profile,
                'client_register': client_register
            })
        return render(request, 'freelancer/ViewProjects.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
            'todos': todos,
            'project_details': project_details
        })
    else:
        return render(request, 'freelancer/PermissionDenied.html',{'profile1':profile1,'profile2':profile2,'freelancer':freelancer})
  
  
  
@login_required
@nocache
def single_project_view(request,pid):
    
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    freelancer=FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission==True:
        todos = Todo.objects.filter(user_id=uid)
        project=Project.objects.get(id=pid)
        uid=project.user_id
        client_profile = ClientProfile.objects.get(user_id=uid)
        client_register = Register.objects.get(user_id=uid)
        return render(request, 'freelancer/SingleProject.html',{'profile1':profile1,'profile2':profile2,'freelancer':freelancer,'todos':todos,'project':project,'client_profile':client_profile,'client_register':client_register})
    else:
        return render(request, 'freelancer/PermissionDenied.html',{'profile1':profile1,'profile2':profile2,'freelancer':freelancer})
        
    
    
 
@login_required
@nocache
def add_new_proposal(request,pid):
    
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2=Register.objects.get(user_id=uid)
    freelancer=FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission==True:
        todos = Todo.objects.filter(user_id=uid)
        project=Project.objects.get(id=pid)
        uid=project.user_id
        client_profile = ClientProfile.objects.get(user_id=uid)
        client_register = Register.objects.get(user_id=uid)
        if request.method == 'POST':
            title = request.POST.get('proposal_title')
            description = request.POST.get('proposal_description')
            file = request.FILES.get('proposal_file')  
            budget = request.POST.get('proposal_budget')
            category = request.POST.get('proposal_category')
            end_date = request.POST.get('proposal_deadline')
            
            proposal = Proposal(
                project=project,
                freelancer=profile1,
                title=title,
                description=description,
                budget=budget,
                proposed_deadline=end_date
            )
            proposal.save()
            return render(request, 'freelancer/SingleProject.html',{'profile1':profile1,'profile2':profile2,'freelancer':freelancer,'todos':todos,'project':project,'client_profile':client_profile,'client_register':client_register})
    else:
        return render(request, 'freelancer/PermissionDenied.html',{'profile1':profile1,'profile2':profile2,'freelancer':freelancer})
         
         
         
         
@login_required
@nocache
def proposal_list(request):
    uid = request.session.get('uid')
    
    if uid is None:
        return redirect('login')

    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        todos = Todo.objects.filter(user_id=uid)
        
        proposals = Proposal.objects.filter(freelancer_id=uid).select_related('project')
        
        project_details = []
        for proposal in proposals:
            project = proposal.project
            client_profile = ClientProfile.objects.get(user_id=project.user_id)
            reg=Register.objects.get(user_id=project.user_id)
            if client_profile.client_type == 'Individual':
                client_name = f"{reg.first_name} {reg.last_name}"
            else:
                client_name = client_profile.company_name
            
            project_details.append({
                'proposal': proposal,  # Include the entire proposal object
                'project': project,
                'client_name': client_name
            })
        
        return render(request, 'freelancer/Proposals.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
            'todos': todos,
            'project_details': project_details
        })
    else:
        return render(request, 'freelancer/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer
        })