

from datetime import datetime
import random
import string
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io
import os
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from client.models import ClientProfile, FreelanceContract, PaymentInstallment, Project, Review,SharedFile, SharedNote,SharedURL,Repository, Task
from core.decorators import nocache
from core.models import CustomUser, Event, Notification, Register

from django.contrib.auth.decorators import login_required

from freelancer.models import FreelancerProfile, Proposal, ProposalFile, Todo

from django.contrib import messages
from django.db.models import Q


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.utils.dateparse import parse_date
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from io import BytesIO
from xhtml2pdf import pisa
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

@login_required
@nocache
def freelancer_view(request):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role != 'freelancer':
        return redirect('login')
        
    uid = request.session['uid']
    logged_user = request.user
    uid = request.user.id
    profile2 = Register.objects.get(user_id=uid)
    todos = Todo.objects.filter(user_id=uid)
    profile1 = CustomUser.objects.get(id=uid)
    notifications = Notification.objects.filter(user=logged_user).order_by('-created_at')[:10]

    current_date = timezone.now().date()
    one_week_later = current_date + timedelta(days=7)
    
    events = Event.objects.filter(
        user=logged_user,
        start_time__range=[current_date, one_week_later]
    ).order_by('start_time')

    total_projects = Project.objects.filter(freelancer=logged_user).count()
    completed_projects = Project.objects.filter(freelancer=logged_user, project_status='Completed').count()
    not_completed_projects = total_projects - completed_projects

    for event in events:
        one_day_before = event.start_time.date() - timedelta(days=1)
        
        if one_day_before == current_date:
            notification_message = f"Reminder: Upcoming event '{event.title}' tomorrow!"
            Notification.objects.get_or_create(
                user=logged_user,
                message=notification_message,
                defaults={'is_read': False}
            )
        
        if event.start_time.date() == current_date:
            notification_message = f"Reminder: Event '{event.title}' is today!"
            Notification.objects.get_or_create(
                user=logged_user,
                message=notification_message,
                defaults={'is_read': False}
            )
    freelancer_projects = Project.objects.filter(freelancer=logged_user)
    project_progress_data = []

    for project in freelancer_projects:
        tasks = Task.objects.filter(project=project)
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='Completed').count()
        progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0.0

        if progress_percentage == 100:
            project.project_status = 'Completed'
            project.save()
        
        client_profile = ClientProfile.objects.get(user=project.user_id)
        if client_profile.client_type == 'Individual':
            register_instance = Register.objects.get(user=project.user_id)

            first_name = register_instance.first_name
            last_name = register_instance.last_name

            client_name = f"{first_name} {last_name}"
        else:
            client_name = client_profile.company_name
        project_progress_data.append({
            'project': project,
            'progress_percentage': progress_percentage,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'client_name': client_name  
        })
        
    if logged_user.is_authenticated and profile2 and not any([
        profile2.phone_number or '',
        profile2.profile_picture or '',
        profile2.bio_description or '',
        profile2.location or ''
    ]):
        return render(request, 'freelancer/Add_profile.html', {
            'profile1': profile1,
            'profile2': profile2,
            'uid': uid,
            'todos': todos,
            'notifications': notifications,
            'events': events
        })
    
    return render(request, 'freelancer/index.html', {
        'profile2': profile2,
        'profile1': profile1,
        'uid': uid,
        'todos': todos,
        'notifications': notifications,
        'events': events,
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'not_completed_projects': not_completed_projects,
        'project_progress_data': project_progress_data,
    })



    
@login_required
@nocache
def tasks_list(request):
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)

    if profile1.permission:
        
        tasks = Task.objects.filter(project__freelancer=profile1).order_by('due_date')

        return render(request, 'freelancer/tasks.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
            'tasks': tasks,  
        })
    else:
        return render(request, 'freelancer/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
        })
        


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
            face_image_bytes = extract_image_from_pdf(aadhaar)
            if face_image_bytes:
                profile.aadhaar_face_image.save('aadhaar_face_image.jpg', ContentFile(face_image_bytes))
        profile.skills = selected_skills
        profile.professional_title = professional_titles
        profile.save()

        return redirect('freelancer:freelancer_view')

    context = {
        'profile': profile,
        'uid': uid,
        'todos': todos,
    }

    return render(request, 'freelancer/Add_profile.html', context)



import fitz  # PyMuPDF
import cv2
import numpy as np
from io import BytesIO
from django.core.files.base import ContentFile

def extract_image_from_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype='pdf')
    
    page = pdf_document.load_page(0)
    images = page.get_images(full=True)
    
    if images:
        xref = images[0][0] 
        base_image = pdf_document.extract_image(xref)
        image_bytes = base_image["image"]
        
        # Convert image bytes to a numpy array
        image_array = np.asarray(bytearray(image_bytes), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # Load a pre-trained face detection model
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Convert image to grayscale for face detection
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face_image = image[y:y+h, x:x+w]
            _, buffer = cv2.imencode('.jpg', face_image)
            return buffer.tobytes()
        
    return None


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
def notification_mark_as_read(request,not_id):
    notification = Notification.objects.get(id=not_id)
    notification.is_read = True
    notification.save()
    next_url = request.GET.get('next', 'freelancer:freelancer_view')
    return redirect(next_url)





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
        messages.success(request, 'Your profile has been changed successfully!')
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
            messages.success(request, 'Your profile picture has been changed successfully!')
            return redirect('freelancer:account_settings')
    return render(request, 'freelancer/accounts.html',{'profile1':profile1,'profile2':profile2,'freelancer':freelancer,'todos':todos,})  


   
        
@login_required
@nocache
def client_list(request):
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)

    if profile1.permission:
        todos = Todo.objects.filter(user_id=uid)
        
        users_with_profiles = CustomUser.objects.filter(role='client').exclude(
            clientprofile__client_type__exact=''
        ).select_related('clientprofile')

        registers = Register.objects.all()
        register_dict = {reg.user_id: reg for reg in registers}  

        
        search_query = request.GET.get('search', '').lower()
        filter_query = request.GET.get('filter', '')

        if search_query:
            users_with_profiles = users_with_profiles.filter(
                Q(clientprofile__company_name__icontains=search_query) |
                Q(register__first_name__icontains=search_query) |
                Q(register__last_name__icontains=search_query) |
                Q(clientprofile__license_number__icontains=search_query)
            )

        if filter_query:
            users_with_profiles = users_with_profiles.filter(clientprofile__client_type=filter_query)
        
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
            'todos': todos,
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
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        profile3 = CustomUser.objects.get(id=cid)
        profile4 = Register.objects.get(user_id=cid)
        client = ClientProfile.objects.get(user_id=cid)
        todos = Todo.objects.filter(user_id=uid)
        
        reviews = Review.objects.filter(reviewee=profile3).order_by('-review_date')

        review_details = []
        for review in reviews:
            
            reviewer_profile = Register.objects.get(user_id=review.reviewer.id)
            
           
            reviewer_name = reviewer_profile.first_name + ' ' + reviewer_profile.last_name
          
            review_details.append({
                'review': review,
                'reviewer_name': reviewer_name,
                'reviewer_image': reviewer_profile.profile_picture.url if reviewer_profile.profile_picture else None,
            })

        return render(request, 'freelancer/SingleClient.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
            'profile3': profile3,
            'profile4': profile4,
            'client': client,
            'todos': todos,
            'reviews': review_details,  # Include reviews in context
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
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role != 'freelancer':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    client = FreelancerProfile.objects.get(user_id=uid)
    events = Event.objects.filter(user=uid)
    events_data = [
        {
            'id': event.id,  # Change this to 'id'
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': (event.end_time + timedelta(days=1)).isoformat(),  
            'description': event.description,
            'color': event.color,
        }
        for event in events
    ]

    if profile1.permission:
        return render(request, 'freelancer/calendar.html', {
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
def add_new_event(request):
    if not request.user.is_authenticated or request.user.role != 'freelancer':
        return redirect('login')

    uid = request.session.get('uid')
    if not uid:
        return redirect('login')

    profile1 = get_object_or_404(CustomUser, id=uid)
    profile2 = get_object_or_404(Register, user_id=uid)
    freelancer = get_object_or_404(FreelancerProfile, user_id=uid)

    if profile1.permission:
        if request.method == 'POST':
            title = request.POST.get('title')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            description = request.POST.get('description')
            color = request.POST.get('color')

            user = request.user
            Event.objects.create(
                title=title,
                start_time=start_time,
                end_time=end_time,
                description=description,
                color=color,
                user=user
            )
            return redirect('freelancer:calendar')  
        
    
    return render(request, 'freelancer/PermissionDenied.html', {
        'profile1': profile1,
        'profile2': profile2,
        'freelancer': freelancer,
    })
    
    
        
@login_required
@nocache
def update_event(request):
    if not request.user.is_authenticated or request.user.role != 'freelancer':
        return redirect('login')

    uid = request.session.get('uid')
    profile1 = get_object_or_404(CustomUser, id=uid)
    profile2 = get_object_or_404(Register, user_id=uid)
    freelancer = get_object_or_404(FreelancerProfile, user_id=uid)

    if profile1.permission:
        if request.method == 'POST':
            event_id = request.POST.get('event_id')
            if not event_id:
              
                return redirect('freelancer:calendar')  

            event = get_object_or_404(Event, id=event_id)

            title = request.POST.get('title')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            description = request.POST.get('description')
            color = request.POST.get('color')

            event.title = title
            event.start_time = start_time
            event.end_time = end_time
            event.description = description
            event.color = color
            
            event.save()

            return redirect('freelancer:calendar')

        

    else:
        return render(request, 'freelancer/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
        })



@login_required
@nocache
def delete_event(request):
    if 'uid' not in request.session or not request.user.is_authenticated or request.user.role != 'freelancer':
        return redirect('login')

    uid = request.session['uid']
    profile1 = get_object_or_404(CustomUser, id=uid)
    profile2 = get_object_or_404(Register, user_id=uid)
    freelancer = get_object_or_404(FreelancerProfile, user_id=uid)

    if profile1.permission:
        if request.method == 'POST':
            event_id = request.POST.get('event_id')
            if not event_id:
                return redirect('freelancer:calendar')  # Handle missing event_id case

            try:
                event = Event.objects.get(id=event_id)
                event.delete()
            except Event.DoesNotExist:
                pass  # Handle case where event does not exist

            return redirect('freelancer:calendar')

        else:
            return redirect('freelancer:calendar')

    else:
        return render(request, 'freelancer/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
        })





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
def update_todo(request):
    uid = request.session.get('uid')
    
    if uid is None:
        return redirect('login')

    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)

    if profile1.permission:
        if request.method == 'POST':
            todo_title = request.POST.get('title')
            todo_id = request.POST.get('todo_id')
            if todo_id:
                todo = get_object_or_404(Todo, id=todo_id)
                todo.title = todo_title
                todo.save()
                return redirect('freelancer:todo')  
        
        return redirect('freelancer:todo') 

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
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        todos = Todo.objects.filter(user_id=uid)


        search = request.GET.get('search', '')
        filter_type = request.GET.get('filter_type', '')
        status = request.GET.get('status', '')
        cat = request.GET.get('category', '')

        print("Category filter value:", cat)
        print("Filter type:", filter_type)
        projects = Project.objects.all()

        if search:
            projects = projects.filter(Q(title__icontains=search) | Q(category__icontains=search))


        if filter_type == 'category' and cat:
            projects = projects.filter(category=cat)


        if filter_type == 'status' and status:
            projects = projects.filter(status=status)


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

        categories = [
    "Web Development","Front-End Development","Back-End Development","Full-Stack Development","Mobile Development",
    "Android Development","iOS Development","UI/UX Design",
    "Graphic Design","Logo Design","Poster Design","Software Development",
    "Machine Learning Engineering","Artificial Intelligence"
]

        return render(request, 'freelancer/ViewProjects.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
            'todos': todos,
            'project_details': project_details,
            'categories': categories
        })
    else:
        return render(request, 'freelancer/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer
        })
  
  
  
@login_required
@nocache
def single_project_view(request, pid):
    uid = request.user.id  # Use request.user.id to get the logged-in user's ID
    
    # Fetch user profiles and project
    profile1 = get_object_or_404(CustomUser, id=uid)
    profile2 = get_object_or_404(Register, user_id=uid)
    freelancer = get_object_or_404(FreelancerProfile, user_id=uid)
    
    if profile1.permission:
        project = get_object_or_404(Project, id=pid)
        client_user_id = project.user_id  
        client_profile = get_object_or_404(ClientProfile, user_id=client_user_id)
        client_register = get_object_or_404(Register, user_id=client_user_id)
        
        proposal_exists = Proposal.objects.filter(freelancer=uid, project_id=pid).exists()
        
        todos = Todo.objects.filter(user_id=uid)
        
        context = {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
            'todos': todos,
            'project': project,
            'client_profile': client_profile,
            'client_register': client_register,
            'proposal_exists': proposal_exists,
        }
        return render(request, 'freelancer/SingleProject.html', context)
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
            budget = request.POST.get('proposal_budget')
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
            reg = Register.objects.get(user_id=project.user_id)
            
            print(f"Proposal: {proposal}, Project: {project}, Client: {reg.first_name} {reg.last_name}")

            if client_profile.client_type == 'Individual':
                client_name = f"{reg.first_name} {reg.last_name}"
            else:
                client_name = client_profile.company_name
            
            project_details.append({
                'proposal': proposal,
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


        
        
@login_required
@nocache        
def generate_proposal(request,pid):
    
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
        userprofile=CustomUser.objects.get(id=uid)
        fancy_id=generate_fancy_proposal_id()
        
        if request.method == 'POST':
            description = request.POST.get('proposal_description')
            budget = request.POST.get('proposal_budget')
            end_date = request.POST.get('proposal_deadline')
            
            proposal = Proposal(
                project=project,
                freelancer=profile1,
                proposal_details=description,
                budget=budget,
                deadline=end_date,
                fancy_num=fancy_id
            )
            proposal.save()
            return redirect('freelancer:proposal_detail1', prop_id=proposal.id)
        return render(request, 'freelancer/template.html',{'profile1':profile1,'profile2':profile2,'freelancer':freelancer,'todos':todos,'project':project,'client_profile':client_profile,'client_register':client_register,'userprofile':userprofile,'number':fancy_id})
    else:
        return render(request, 'freelancer/PermissionDenied.html',{'profile1':profile1,'profile2':profile2,'freelancer':freelancer})
         
     
  
from django.core.files.base import ContentFile

from bs4 import BeautifulSoup

@login_required
@nocache
def proposal_detail1(request, prop_id):
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)
    proposal = get_object_or_404(Proposal, id=prop_id)
    project = Project.objects.get(id=proposal.project_id)
    client_profile = ClientProfile.objects.get(user_id=project.user_id)
    client_register = Register.objects.get(user_id=project.user_id)
    userprofile = CustomUser.objects.get(id=project.user_id)

    if profile1.permission:
        todos = Todo.objects.filter(user_id=uid)

        if request.method == 'POST':
            # Handle additional file uploads
            files = request.FILES.getlist('additional_files[]')
            for file in files:
                ProposalFile.objects.create(proposal=proposal, file=file)

            pdf_file = request.FILES.get('proposal_pdf')
            if pdf_file:
                proposal.proposal_file.save(f'proposal_{proposal.id}.pdf', pdf_file)
                proposal.save()

            return redirect('freelancer:view_created_proposals')

        return render(request, 'freelancer/proposal_preview.html', {
            'proposal': proposal,
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
            'client_profile': client_profile,
            'client_register': client_register,
            'userprofile': userprofile
        })

    return render(request, 'freelancer/PermissionDenied.html', {
        'profile1': profile1,
        'profile2': profile2,
        'freelancer': freelancer
    })


def generate_fancy_proposal_id(length=4):
    digits = string.digits  # Digits only
    proposal_id = '#'+''.join(random.choices(digits, k=length))
    return proposal_id




@login_required
@nocache
def proposal_detail2(request, prop_id):
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)
    proposal = get_object_or_404(Proposal, id=prop_id)
    project = Project.objects.get(id=proposal.project_id)
    client_profile = ClientProfile.objects.get(user_id=project.user_id)
    client_register = Register.objects.get(user_id=project.user_id)
    userprofile = CustomUser.objects.get(id=project.user_id)

    if profile1.permission:
        todos = Todo.objects.filter(user_id=uid)

        return render(request, 'freelancer/single_proposal.html', {
            'proposal': proposal,
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
            'client_profile': client_profile,
            'client_register': client_register,
            'userprofile': userprofile
        })

    return render(request, 'freelancer/PermissionDenied.html', {
        'profile1': profile1,
        'profile2': profile2,
        'freelancer': freelancer
    })


        
        

@login_required
@nocache
def view_created_proposals(request):
    uid = request.session.get('uid')
    
    if uid is None:
        return redirect('login')

    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        todos = Todo.objects.filter(user_id=uid)
        proposals = Proposal.objects.filter(freelancer=uid).select_related('project')
        
        project_details = []
        for proposal in proposals:
            project = proposal.project
            client_profile = get_object_or_404(ClientProfile, user_id=project.user_id)
            client_register = get_object_or_404(Register, user_id=project.user_id)
            
            try:
                contract = FreelanceContract.objects.get(project=project)
                installments = PaymentInstallment.objects.filter(contract=contract)
            except FreelanceContract.DoesNotExist:
                contract = None
                installments = None
            
            project_details.append({
                'proposal': proposal,
                'project': project,
                'client_profile': client_profile,
                'client_register': client_register,
                'contract': contract,
                'installments': installments
            })

        return render(request, 'freelancer/proposals_created.html', {
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







@login_required
@nocache
def edit_created_proposal(request, prop_id):
    uid = request.session.get('uid')
    
    if uid is None:
        return redirect('login')

    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)
    proposal = get_object_or_404(Proposal, id=prop_id)
    project = Project.objects.get(id=proposal.project_id)
    client_profile = ClientProfile.objects.get(user_id=project.user_id)
    client_register = Register.objects.get(user_id=project.user_id)
    userprofile = CustomUser.objects.get(id=project.user_id)
    
    if profile1.permission:
        todos = Todo.objects.filter(user_id=uid)
        
        if request.method == 'POST':
            # Update proposal details
            description = request.POST.get('proposal_description')
            budget = request.POST.get('proposal_budget')
            end_date = request.POST.get('proposal_deadline')

            if description:
                proposal.proposal_details = description
            if budget:
                proposal.budget = budget
            if end_date:
                proposal.deadline = end_date
            
            # Handle additional file uploads
            if 'additional_files[]' in request.FILES:
                files = request.FILES.getlist('additional_files[]')
                for file in files:
                    # Save the new file
                    ProposalFile.objects.create(proposal=proposal, file=file)

            # Save the uploaded PDF file if present
            pdf_file = request.FILES.get('proposal_pdf')
            if pdf_file:
                proposal.proposal_file.save(f'proposal_{proposal.id}.pdf', pdf_file)
            
            proposal.save()
            return redirect('freelancer:view_created_proposals')
        
        return render(request, 'freelancer/edit_proposal_template.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
            'todos': todos,
            'proposal': proposal,
            'client_profile': client_profile,
            'client_register': client_register,
            'userprofile': userprofile,
            'edit_mode': True
        })
    
    return render(request, 'freelancer/PermissionDenied.html', {
        'profile1': profile1,
        'profile2': profile2,
        'freelancer': freelancer
    })
        
   
   
   
        
@login_required
@nocache
def download_proposal_pdf(request, prop_id):
    uid = request.session.get('uid')
    
    if uid is None:
        return redirect('login')

    proposal = Proposal.objects.get(id=prop_id)
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)

    
    template_path = 'freelancer/proposal_preview.html'  

    
    template = get_template(template_path)
    context = {
        'proposal': proposal,
        'profile2': profile2,
        'freelancer': freelancer,
        'profile1': profile1,
        'edit_mode': False, 
    }
    html = template.render(context)

    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="proposal.pdf"'

    
    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


      
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
    
    register_info = Register.objects.get(user_id=uid)
    first_name = register_info.first_name
    last_name = register_info.last_name
    name = f"{first_name} {last_name}"
    
    context = {
        'user_name': name
    }
    html_content = render_to_string('freelancer/deactivation.html', context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()
    return redirect('login')




@login_required
@nocache
def view_repository(request, repo_id):
    if not request.user.is_authenticated or request.user.role != 'freelancer':
        return redirect('login')

    uid = request.user.id
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        repository = get_object_or_404(Repository, id=repo_id)
        project = get_object_or_404(Project, id=repository.project_id)
        client_profile = ClientProfile.objects.get(user_id=project.user_id)
        client_register = Register.objects.get(user_id=project.user_id)
        
        if client_profile.client_type == 'Individual':
            client_name = f"{client_register.first_name} {client_register.last_name}"
        else:
            client_name = client_profile.company_name
        
        client_profile_picture = client_register.profile_picture if client_register.profile_picture else None

        shared_files = SharedFile.objects.filter(repository=repository).values(
            'file', 'uploaded_at', 'uploaded_by', 'description'
        )
        shared_urls = SharedURL.objects.filter(repository=repository).values(
            'url', 'shared_at', 'shared_by', 'description'
        )
        proposals = Proposal.objects.filter(project=project,status='Accepted')
        contracts = FreelanceContract.objects.filter(project=project)
        items = []
        
        for file in shared_files:
            items.append({
                'type': 'file',
                'url': file['file'],  # Use 'url' for the file URL
                'path': file['file'].split('/')[-1],  # Extract the file name from the path
                'date': file['uploaded_at'],
                'uploaded_by': file['uploaded_by'],
                'description': file['description']
            })
        
        for url in shared_urls:
            items.append({
                'type': 'url',
                'path': url['url'],
                'date': url['shared_at'],
                'shared_by': url['shared_by'],
                'description': url['description']
            })
        
        items.sort(key=lambda x: x['date'])
        notes = SharedNote.objects.filter(repository=repository).order_by('added_at')
        tasks=Task.objects.filter(project=project)
        return render(request, 'freelancer/SingleRepository.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
            'repository': repository,
            'items': items,
             'notes':notes,
            'tasks':tasks,
            'client_name': client_name,
            'client_profile_picture': client_profile_picture,
            'proposals': proposals,
            'contracts': contracts,
            
            'project': project,
        })
    else:
        return render(request, 'freelancer/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
        })


@login_required
@nocache
def add_file(request, repo_id):
    if not request.user.is_authenticated or request.user.role != 'freelancer':
        return redirect('login')

    uid = request.user.id
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        repository = get_object_or_404(Repository, id=repo_id)
        if request.method == 'POST':
            file = request.FILES['files']
            description = request.POST.get('description')
            newfile = SharedFile(
                file=file,
                repository=repository,
                description=description,
                uploaded_by=request.user
            )
            newfile.save()

            messages.success(request, 'Files added successfully.')
            return redirect('freelancer:view_repository', repo_id=repository.id)
    else:
        return render(request, 'freelancer/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
        })

@login_required
@nocache
def add_url(request, repo_id):
    if not request.user.is_authenticated or request.user.role != 'freelancer':
        return redirect('login')

    uid = request.user.id
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        repository = get_object_or_404(Repository, id=repo_id)
        if request.method == 'POST':
            url = request.POST.get('url')
            description = request.POST.get('description')
            newurl = SharedURL(
                url=url,
                repository=repository,
                description=description,
                shared_by=request.user
            )
            newurl.save()

            messages.success(request, 'URL added successfully.')
            return redirect('freelancer:view_repository', repo_id=repository.id)
    else:
        return render(request, 'freelancer/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
        })

@login_required
@nocache
def add_note(request, repo_id):
    if not request.user.is_authenticated or request.user.role != 'freelancer':
        return redirect('login')

    uid = request.user.id
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        repository = get_object_or_404(Repository, id=repo_id)
        if request.method == 'POST':
            file = request.FILES['files']
            description = request.POST.get('description')
            newfile = SharedFile(
                file=file,
                repository=repository,
                description=description,
                uploaded_by=request.user
            )
            newfile.save()

            messages.success(request, 'Files added successfully.')
            return redirect('freelancer:view_repository', repo_id=repository.id)
    else:
        return render(request, 'freelancer/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
        })



@login_required
def update_freelancer_signature(request):
    if not request.user.is_authenticated or request.user.role != 'freelancer':
        return redirect('login')

    uid = request.user.id
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        if request.method == 'POST':
            contract_id=request.POST.get('contract')
            contract = get_object_or_404(FreelanceContract, id=contract_id, freelancer=request.user)
            file = request.FILES.get('freelancer_signature')
            if file:
                contract.freelancer_signature = file
                contract.save()

            messages.success(request, 'Signature added successfully.')
            return redirect('freelancer:view_contract', cont_id=contract_id)
    else:
        return render(request, 'freelancer/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
        })





@login_required
@nocache
def view_contract(request, cont_id):
    if 'uid' not in request.session:
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    freelancer = FreelancerProfile.objects.get(user_id=uid)

    if profile1.permission:
        contract = FreelanceContract.objects.filter(id=cont_id).first()
        if contract:
            payment_installments = PaymentInstallment.objects.filter(contract=contract)
            client_profile = contract.project.user.clientprofile  
            client_register = contract.project.user.register  
            project_details = contract.project  

            accepted_proposal = Proposal.objects.filter(project=project_details, status='accepted').first()

            context = {
                'profile1': profile1,
                'profile2': profile2,
                'freelancer': freelancer,
                'detail': {
                    'contract': contract,
                    'project': project_details,
                    'client_profile': client_profile,
                    'client_register': client_register,
                    'proposal': accepted_proposal,
                    'installments': payment_installments,
                }
            }
            return render(request, 'freelancer/ViewContract.html', context)
    else:
        return render(request, 'freelancer/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
        })



@csrf_exempt
def upload_pdf(request):
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf')
        contract_id = request.POST.get('contract_id')

        if pdf_file and contract_id:
            try:
                contract = FreelanceContract.objects.get(id=contract_id)
                
                if contract.pdf_version:
                    return JsonResponse({'status': 'exists', 'message': 'File already exists'}, status=400)
                
                contract.pdf_version.save(pdf_file.name, pdf_file)
                contract.save()
                return JsonResponse({'status': 'success'})
            
            except FreelanceContract.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Contract not found'}, status=404)
        
        return JsonResponse({'status': 'error', 'message': 'Invalid file or contract ID'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)



@login_required
@nocache
def submit_user_review(request):
    if request.method == 'POST':
        review_text = request.POST.get('review')
        reviewer_id = request.user.id
        client_id = request.POST.get('client_id')
        project_id = int(request.POST.get('project_id'))
        overall_rating = int(request.POST.get('overall_rating'))
        client_id = int(client_id)
        
        # Debugging prints
        print(f"Review Text: {review_text}")
        print(f"Reviewer ID: {reviewer_id}")
        print(f"Reviewee ID: {client_id}")
        print(f"Project ID: {project_id}")
        print(f"Overall Rating: {overall_rating}S")

        # Fetch the related objects
        try:
            project = get_object_or_404(Project, id=project_id)
            freelancer = get_object_or_404(CustomUser, id=reviewer_id)
            client = get_object_or_404(CustomUser, id=client_id)
        except Exception as e:
            print(f"Error fetching data: {e}")
            return HttpResponse(status=404, content=f"Error: {e}")

        print(f"Project: {project}")
        print(f"Freelancer: {freelancer}")
        print(f"Client: {client}")

        # Create and save the review
        review = Review(
            reviewer=freelancer,
            reviewee=client,
            project=project,
            overall_rating=overall_rating,
            review_text=review_text
        )
        review.save()

        print("Review saved successfully.")

        if project.freelancer and project.freelancer == freelancer:
            project.freelancer_review_given = True
            project.save()
            print(f"Project updated with freelancer review: {project.freelancer_review_given}")
        else:
            print(f"Freelancer ID mismatch. Expected: {project.freelancer.id}, Found: {freelancer.id}")


        return redirect('freelancer:freelancer_view')

    return HttpResponse(status=405, content="Method Not Allowed")