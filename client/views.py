

import datetime
from django.contrib import messages
from django.shortcuts import redirect, render
import razorpay

from client.models import ClientProfile, FreelanceContract, PaymentInstallment, Project, Review, SharedFile, SharedNote, SharedURL, Task
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
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

@login_required
@nocache
def client_view(request):
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('login')

    logged_user = request.user
    current_date = datetime.date.today()
    one_week_later = current_date + datetime.timedelta(days=7)

    events = Event.objects.filter(user=logged_user, start_time__range=[current_date, one_week_later])

    profile1 = CustomUser.objects.get(id=logged_user.id)
    profile2 = Register.objects.get(user_id=logged_user.id)
    notifications = Notification.objects.filter(user=logged_user).order_by('-created_at')[:10]

    for event in events:
        one_day_before = event.start_time.date() - datetime.timedelta(days=1)
        if one_day_before == current_date:
            Notification.objects.get_or_create(
                user=logged_user,
                message=f"Reminder: Upcoming event '{event.title}' tomorrow!",
                defaults={'is_read': False}
            )
        if event.start_time.date() == current_date:
            Notification.objects.get_or_create(
                user=logged_user,
                message=f"Reminder: Event '{event.title}' is today!",
                defaults={'is_read': False}
            )

    client_projects = Project.objects.filter(user=logged_user)
    project_progress_data = []

    # Project progress data
    for project in client_projects:
        tasks = Task.objects.filter(project=project)
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='Completed').count()
        progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0.0

        if progress_percentage == 100:
            project.project_status = 'Completed'
            project.save()
            
        project_progress_data.append({
            'project': project,
            'progress_percentage': progress_percentage,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks
        })

    total_projects = client_projects.count()
    completed_projects = client_projects.filter(project_status='Completed').count()
    not_completed_projects = total_projects - completed_projects
    
    client_contracts = FreelanceContract.objects.filter(client=logged_user).select_related('freelancer', 'project')
    payment_installments = PaymentInstallment.objects.filter(contract__in=client_contracts).select_related('contract__project', 'contract__freelancer')

    for installment in payment_installments:
        due_date = installment.due_date
        one_day_before_due = due_date - datetime.timedelta(days=1)
        
        if installment.status == 'Pending':
            if one_day_before_due == current_date:
                Notification.objects.get_or_create(
                    user=logged_user,
                    message=f"Reminder: Payment installment for project '{installment.contract.project.title}' is due tomorrow!",
                    defaults={'is_read': False}
                )
            elif due_date == current_date:
                Notification.objects.get_or_create(
                    user=logged_user,
                    message=f"Reminder: Payment installment for project '{installment.contract.project.title}' is due today!",
                    defaults={'is_read': False}
                )

    if not profile2.phone_number and not profile2.profile_picture and not profile2.bio_description and not profile2.location:
        return render(request, 'Client/Add_profile.html', {
            'profile2': profile2,
            'profile1': profile1,
            'uid': logged_user.id,
            'notifications': notifications,
            'events': events
        })

    return render(request, 'Client/index.html', {
        'profile2': profile2,
        'profile1': profile1,
        'uid': logged_user.id,
        'notifications': notifications,
        'events': events,
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'not_completed_projects': not_completed_projects,
        'project_progress_data': project_progress_data,
        'payment_installments': payment_installments
    })







client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
@nocache
def make_payment(request, installment_id):
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('login')

    uid = request.user.id
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    client = ClientProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        if request.method == 'POST':
            installment = get_object_or_404(PaymentInstallment, id=installment_id)
            
            if installment.status == 'paid':
                return JsonResponse({'status': 'error', 'message': 'This installment has already been paid.'})
            
            # Create Razorpay order
            order_amount = int(installment.amount * 100)  # Convert to paise
            order_currency = 'INR'
            order_receipt = f'installment_{installment.id}'
            
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            try:
                order = client.order.create({
                    'amount': order_amount,
                    'currency': order_currency,
                    'receipt': order_receipt,
                    'payment_capture': '1'
                })
                installment.razorpay_order_id = order['id']
                installment.save()
                response_data = {
                    'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                    'order_id': order['id'],
                    'amount': order_amount,
                    'currency': order_currency,
                    'installment_id': installment.id,
                }
                
                return JsonResponse(response_data)
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })


@csrf_exempt
def verify_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        payment_id = data.get('razorpay_payment_id')
        order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')

        if not (payment_id and order_id and signature):
            return JsonResponse({'status': 'error', 'message': 'Missing parameters'})

        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            client.utility.verify_payment_signature(params_dict)
            installment = get_object_or_404(PaymentInstallment, razorpay_order_id=order_id)
            installment.status = 'paid'
            installment.razorpay_payment_id = payment_id
            installment.paid_at=timezone.now().date()
            installment.save()
            
            return JsonResponse({'status': 'success'})
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'status': 'error', 'message': 'Payment verification failed: Signature mismatch'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



def payment_success(request):
    installment_id = request.GET.get('installment_id')
    
    if not installment_id:
        return HttpResponse("No installment ID provided.", status=400)
    
    installment = get_object_or_404(PaymentInstallment, id=installment_id)
    
    installment.status = 'paid'
    installment.save()

    return render(request, 'client/success.html', {'installment': installment})


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
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role != 'client':
        return redirect('login')

    uid = request.session.get('uid', uid)  # Retrieve uid from session if not passed in URL
    profile = Register.objects.get(user_id=uid)
    client_profile, created = ClientProfile.objects.get_or_create(user_id=uid)

    if request.method == 'POST':
        # Fetching data from POST request
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
        website = request.POST.get('company_website')
        aadhar = request.FILES.get('aadhar')
        license_number = request.POST.get('license_number')  # CIN number

        # Update Register profile
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
            client_profile.website = website
            client_profile.license_number = license_number  # Save CIN number
            client_profile.aadhaar_document = ''
        else:
            client_profile.company_name = ''
            client_profile.website = ''
            client_profile.license_number = ''
            client_profile.aadhaar_document = aadhar
        client_profile.save()

        return redirect('client:client_view')

    return render(request, 'client/add_profile_client.html', {'profile': profile, 'client_profile': client_profile})


@login_required
@nocache   
def update_profile(request, uid):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role != 'client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    client = ClientProfile.objects.get(user_id=uid)

    if request.method == 'POST':
        # Fetch POST data
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        phone_number = request.POST.get('phone_number')
        bio_description = request.POST.get('bio_description')
        location = request.POST.get('location')
        linkedin = request.POST.get('linkedin')
        instagram = request.POST.get('instagram')
        twitter = request.POST.get('twitter')
        license_number = request.POST.get('license_number')
        company_name = request.POST.get('company_name')
        website = request.POST.get('company_website')
        aadhar = request.FILES.get('aadhar')

        # Update Register model fields
        profile2.first_name = first_name
        profile2.last_name = last_name
        profile2.phone_number = phone_number
        profile2.bio_description = bio_description
        profile2.location = location
        profile2.linkedin = linkedin
        profile2.instagram = instagram
        profile2.twitter = twitter
        profile2.save()

        # Update ClientProfile model fields
        client_type = client.client_type
        if client_type == 'Company':
            client.company_name = company_name
            client.website = website
            client.license_number = license_number
            client.aadhaar_document = ''
        else:
            client.company_name = ''
            client.website = ''
            client.license_number = ''
            client.aadhaar_document = aadhar

        client.save()

        return redirect('client:account_settings')

    return render(request, 'client/profile.html', {'profile1': profile1, 'profile2': profile2, 'client': client})



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
        ).select_related('freelancerprofile', 'register')

        if search_query:
            users_with_profiles = users_with_profiles.filter(
                Q(username__icontains=search_query) |
                Q(freelancerprofile__professional_title__icontains=search_query) |
                Q(register__first_name__icontains=search_query) |
                Q(register__last_name__icontains=search_query)
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
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role != 'client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    client = ClientProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        profile3 = CustomUser.objects.get(id=fid)
        profile4 = Register.objects.get(user_id=fid)
        freelancer = FreelancerProfile.objects.get(user_id=fid)
        
        skills_list = [skill.strip() for skill in freelancer.skills.strip('[]').replace("'", "").split(',')]
        
        reviews = Review.objects.filter(reviewee=profile3).order_by('-review_date')

        review_details = []
        for review in reviews:
            reviewer_profile = Register.objects.get(user_id=review.reviewer.id)
            
            if review.reviewer.clientprofile.client_type == 'Individual':
                reviewer_name = reviewer_profile.first_name + ' ' + reviewer_profile.last_name
            else:
                reviewer_name = review.reviewer.clientprofile.company_name
            
            review_details.append({
                'review': review,
                'reviewer_name': reviewer_name,
                'reviewer_image': reviewer_profile.profile_picture.url if reviewer_profile.profile_picture else None,
            })

        return render(request, 'client/SingleFreelancer.html', {
            'profile1': profile1,
            'profile2': profile2,
            'freelancer': freelancer,
            'client': client,
            'profile3': profile3,
            'profile4': profile4,
            'skills': skills_list,  
            "reviews": review_details,
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
                return redirect('client:calendar')  
            try:
                event = Event.objects.get(id=event_id)
                event.delete()
            except Event.DoesNotExist:
                pass  
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

        


from django.utils.dateparse import parse_date
        
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

            end_date = parse_date(end_date)
            project.title = title
            project.description = description
            project.budget = budget
            project.category = category
            project.allow_bid = allow_bid
            project.end_date = end_date
            project.file_upload = file_upload
            project.status='open'
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
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role != 'client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    client = ClientProfile.objects.get(user_id=uid)
    if profile1.permission:
        projects = Project.objects.filter(user_id=uid).select_related('freelancer')
        freelancer_names = {}
        project_repos = {}

        for project in projects:
            if project.freelancer:
                register = Register.objects.filter(user=project.freelancer).first()
                if register:
                    full_name = f"{register.first_name} {register.last_name}"
                    freelancer_names[project.id] = full_name
                else:
                    freelancer_names[project.id] = 'No name available'
            else:
                freelancer_names[project.id] = 'No freelancer assigned'
                
            repository = Repository.objects.filter(project=project).first()
            project_repos[project.id] = repository.id if repository else None

        # Debugging information
        print("Projects:", projects)
        print("Freelancer Names:", freelancer_names)
        print("Project Repos:", project_repos)



        return render(request, 'client/ProjectList.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
            'projects': projects,
            'freelancer_names': freelancer_names,
            'project_repos': project_repos,
        })
    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })

        


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
                project.freelancer = proposal.freelancer
                project.budget = proposal.budget
                project.project_status='In Progress'
                project.status='closed'
                project.start_date=timezone.now().date()
                
                gst_rate = 18 
                gst_amount = project.budget * gst_rate / 100
                total_including_gst = project.budget + gst_amount
                
                project.gst_amount = gst_amount
                project.total_including_gst = total_including_gst
                project.save()
                project.save()
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



from client.models import Repository
from django.contrib import messages

@login_required
@nocache
def create_repository(request):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role != 'client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    client = ClientProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        if request.method == 'POST':
            title = request.POST.get('repoName')
            project_id = request.POST.get('project_id')
            project = get_object_or_404(Project, id=project_id)

            if title:
                if Repository.objects.filter(name__iexact=title).exists():
                    messages.error(request, 'A repository with this name already exists for this project.')
                    return redirect('client:project_list')  

                repository = Repository.objects.create(
                    name=title,
                    project=project,
                    created_by=request.user
                )
                if repository:
                    freelancer = project.freelancer 
                    Notification.objects.get_or_create(
                        user=freelancer,  
                        message=f"A new repository '{title}' has been created for the project '{project.title}'.",
                        is_read=False
                    )

                messages.success(request, 'Repository created successfully.')
                return redirect('client:project_list')
        
    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })
        
 
@login_required
@nocache
def view_repository(request, repo_id):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role != 'client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    client = ClientProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        repository = get_object_or_404(Repository, id=repo_id)
        project = get_object_or_404(Project, id=repository.project_id)
        freelancer_name = None
        freelancer_profile_picture = None

        if project.freelancer_id:
            freelancer_register = Register.objects.get(user_id=project.freelancer_id)
            freelancer_name = f"{freelancer_register.first_name} {freelancer_register.last_name}"
            freelancer_profile_picture = freelancer_register.profile_picture if freelancer_register.profile_picture else None

        shared_files = SharedFile.objects.filter(repository=repository).values(
            'file', 'uploaded_at', 'uploaded_by', 'description'
        )
        shared_urls = SharedURL.objects.filter(repository=repository).values(
            'url', 'shared_at', 'shared_by', 'description'
        )
        notes = SharedNote.objects.filter(repository=repository).order_by('added_at')
        tasks = Task.objects.filter(project=project)

        proposals = Proposal.objects.filter(project=project,status='Accepted')
        contracts = FreelanceContract.objects.filter(project=project)

        items = []
        
        for file in shared_files:
            items.append({
                'type': 'file',
                'path': file['file'],
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
    
        return render(request, 'client/SingleRepository.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
            'repository': repository,
            'items': items,
            'notes': notes,
            'tasks': tasks,
            'freelancer_name': freelancer_name,
            'freelancer_profile_picture': freelancer_profile_picture,
            'proposals': proposals,
            'contracts': contracts,
            'project': project,
        })
        
    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })







@login_required
@nocache
def add_github_link(request,repo_id):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role != 'client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    client = ClientProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        repository = get_object_or_404(Repository, id=repo_id)
        if request.method=='POST':
            project_id = request.POST.get('project_id')  # Get the project_id from the hidden field
            git_repo_link = request.POST.get('git_repo_link')
            
            if git_repo_link:
                project = get_object_or_404(Project, id=project_id)
                project.git_repo_link = git_repo_link
                project.save()
                messages.success(request, 'GitHub repository link updated successfully!')
            else:
                messages.error(request, 'Failed to update GitHub repository link.')

                messages.success(request, 'Files added successfully.')
            return redirect('client:view_repository', repo_id=repository.id)
        
    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })       




@login_required
@nocache
def add_file(request,repo_id):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role != 'client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    client = ClientProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        repository = get_object_or_404(Repository, id=repo_id)
        if request.method=='POST':
            file = request.FILES['files']
            description=request.POST.get('description')
            newfile = SharedFile(
                    file=file,
                    repository=repository,
                    description=description,
                    uploaded_by=request.user)
            newfile.save()

            messages.success(request, 'Files added successfully.')
            return redirect('client:view_repository', repo_id=repository.id)
        
    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })       





@login_required
@nocache
def add_url(request,repo_id):
    if 'uid' not in request.session and not request.user.is_authenticated and request.user.role != 'client':
        return redirect('login')

    uid = request.session['uid']
    profile1 = CustomUser.objects.get(id=uid)
    profile2 = Register.objects.get(user_id=uid)
    client = ClientProfile.objects.get(user_id=uid)
    
    if profile1.permission:
        repository = get_object_or_404(Repository, id=repo_id)
        if request.method=='POST':
            url = request.POST.get('url')
            description=request.POST.get('description')
            newurl = SharedURL(
                    url=url,
                    repository=repository,
                    description=description,
                    shared_by=request.user)
            newurl.save()

            messages.success(request, 'URL added successfully.')
            return redirect('client:view_repository', repo_id=repository.id)
        
    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })       





@login_required
@nocache
def add_note(request, repo_id):
    # Check if user has required permission
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('login')

    # Fetch user profiles
    profile1 = CustomUser.objects.get(id=request.user.id)
    profile2 = Register.objects.get(user_id=request.user.id)
    client = ClientProfile.objects.get(user_id=request.user.id)
    
    if profile1.permission:
        repository = get_object_or_404(Repository, id=repo_id)
        if request.method == 'POST':
            note_content = request.POST.get('content')
            print(f"Note Content: {note_content}")  
            if note_content:
                new_note=SharedNote(
                    repository=repository,  
                    note=note_content,
                    added_by=request.user
                )
                new_note.save()
                messages.success(request, 'Note added successfully.')
                return redirect('client:view_repository', repo_id=repository.id)
            else:
                messages.error(request, 'Note content cannot be empty.')
        
    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })

    return redirect('client:view_repository', repo_id=repo_id) 




@login_required
@nocache
def add_task(request, repo_id):
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('login')

    profile1 = CustomUser.objects.get(id=request.user.id)
    profile2 = Register.objects.get(user_id=request.user.id)
    client = ClientProfile.objects.get(user_id=request.user.id)
    
    if profile1.permission:
        repository = get_object_or_404(Repository, id=repo_id)
        project = repository.project
        if request.method == "POST":
            title = request.POST.get('title')
            description = request.POST.get('description')
            start_date = request.POST.get('start_date')
            due_date = request.POST.get('due_date')

            task = Task.objects.create(
            project=project,
            title=title,
            description=description,
            start_date=start_date,
            due_date=due_date,
        )
        task.save()

    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })

    return redirect('client:view_repository', repo_id=repo_id) 



@login_required
@nocache
def update_task_progress(request, repo_id):
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('login')

    profile1 = CustomUser.objects.get(id=request.user.id)
    profile2 = Register.objects.get(user_id=request.user.id)
    client = ClientProfile.objects.get(user_id=request.user.id)
    
    if profile1.permission:
        if request.method == "POST":
            progress_percentage = request.POST.get('progress_percentage')
            task_id = request.POST.get('task_id')

            
            progress = int(progress_percentage)
            task = Task.objects.get(id=task_id)
            task.progress_percentage = progress
            
            # Debugging output
            print(f"Task ID: {task_id}")
            print(f"New Progress: {progress}")

            if progress >= 100:
                task.status = 'Completed'
            else:
                task.status = 'In Progress'  # Assuming you want to set a different status for progress < 100
            
            task.save()

            return redirect('client:view_repository', repo_id=repo_id) 

    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })

    return redirect('client:view_repository', repo_id=repo_id)









@login_required
@nocache
def update_task_status(request, repo_id):
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('login')

    profile1 = CustomUser.objects.get(id=request.user.id)
    profile2 = Register.objects.get(user_id=request.user.id)
    client = ClientProfile.objects.get(user_id=request.user.id)
    
    if profile1.permission:
        if request.method == "POST":
           
            task_id = request.POST.get('task_id')
            new_status = request.POST.get('status')
            
            task = Task.objects.get(id=task_id)
            task.status = new_status
            if new_status== 'Completed':
                task.progress_percentage = 100
                
            task.save()

            return redirect('client:view_repository', repo_id=repo_id) 

    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })

    return redirect('client:view_repository', repo_id=repo_id)






@login_required
@nocache
def edit_task(request, repo_id):
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('login')

    profile1 = CustomUser.objects.get(id=request.user.id)
    profile2 = Register.objects.get(user_id=request.user.id)
    client = ClientProfile.objects.get(user_id=request.user.id)
    
    if profile1.permission:
        if request.method == "POST":
            task_id = request.POST.get('task_id')
            title = request.POST.get('title')
            description = request.POST.get('description')
            start_date = request.POST.get('start_date')
            due_date = request.POST.get('due_date')

            task = get_object_or_404(Task, id=task_id)

            task.title = title
            task.description = description
            task.start_date = start_date
            task.due_date = due_date

            task.save()

            return redirect('client:view_repository', repo_id=repo_id) 

    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })

    return redirect('client:view_repository', repo_id=repo_id)



@login_required
@nocache
def submit_contract(request, pro_id):
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('login')

    profile1 = get_object_or_404(CustomUser, id=request.user.id)
    profile2 = get_object_or_404(Register, user_id=request.user.id)
    client = get_object_or_404(ClientProfile, user_id=request.user.id)
    
    if profile1.permission:
        project = Project.objects.get(id=pro_id) 
        freelancer = project.freelancer 
        freelancer_data = Register.objects.get(user_id=freelancer)
        freelancer_name = f"{freelancer_data.first_name} {freelancer_data.last_name}"
        proposal = Proposal.objects.get(project=project, freelancer=project.freelancer)

        existing_contract = FreelanceContract.objects.filter(client=profile1, project=project).first()

        if request.method == 'POST' and not existing_contract:
            client_instance = CustomUser.objects.get(id=request.POST.get('client_id'))
            freelancer_instance = CustomUser.objects.get(id=request.POST.get('freelancer_id'))
            signature = request.FILES.get('client_signature')
            project_instance = Project.objects.get(id=request.POST.get('project_id'))

            contract = FreelanceContract(
                client=client_instance,
                freelancer=freelancer_instance,
                project=project_instance,
                client_signature=signature
            )
            contract.save()

            amounts = request.POST.getlist('installment_amount[]')
            due_dates = request.POST.getlist('installment_due_date[]')

            for amount, due_date in zip(amounts, due_dates):
                PaymentInstallment.objects.create(contract=contract, amount=amount, due_date=due_date)

            Notification.objects.create(
                user=freelancer_instance,
                message=f'You have received a new agreement for the project "{project.title}" from the client.'
            )
            return redirect('client:project_list')

        payment_installments = PaymentInstallment.objects.filter(contract=existing_contract) if existing_contract else None
        
        return render(request, 'client/Agreement_template.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
            'project': project,
            'freelancer_name': freelancer_name,
            'proposal': proposal,
            'freelancer': freelancer_data,
            'existing_contract': existing_contract,  # Pass existing contract to the template
            'payment_installments': payment_installments,  # Pass payment installments to the template
        })
    else:
        return render(request, 'client/PermissionDenied.html', {
            'profile1': profile1,
            'profile2': profile2,
            'client': client,
        })



@login_required
def submit_review(request):
    if request.method == 'POST':
        quality_of_work = float(request.POST.get('quality_of_work'))
        communication = float(request.POST.get('communication'))
        adherence_to_deadlines = float(request.POST.get('adherence_to_deadlines'))
        professionalism = float(request.POST.get('professionalism'))
        problem_solving_ability = float(request.POST.get('problem_solving_ability'))
        review_text = request.POST.get('review')
        reviewer_id = request.user.id
        reviewee_id = int(request.POST.get('freelancer_id'))
        project_id = int(request.POST.get('project_id'))

        overall_rating = (quality_of_work + communication + adherence_to_deadlines + professionalism + problem_solving_ability) / 5

        review = Review(
            reviewer_id=reviewer_id,
            reviewee_id=reviewee_id,
            project_id=project_id,
            quality_of_work=quality_of_work,
            communication=communication,
            adherence_to_deadlines=adherence_to_deadlines,
            professionalism=professionalism,
            problem_solving_ability=problem_solving_ability,
            overall_rating=overall_rating,
            review_text=review_text
        )
        review.save()
        project = Project.objects.get(id=project_id)
        if project.user.id == reviewer_id:
            project.client_review_given = True
            project.save()
        return redirect('client:client_view')
