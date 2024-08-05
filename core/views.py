
import math
import os
import random
import uuid
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import render,redirect
from .models import EmailVerification, PasswordReset, CustomUser, Register
from django.core.mail import EmailMessage
from django.contrib import messages
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout 
from freelancer.views import freelancer_view
from client.views import client_view
from administrator.views import admin_view
from urllib.parse import urlparse, parse_qs, urlunparse
from urllib.parse import urlencode

def index(request):
    #CustomUser.objects.get(id=3).delete()
    
    if request.user.is_authenticated or 'uid' in request.session:
        uid=request.user
        print(uid)
        return redirect_based_on_user_type(request, request.user)
    return render(request,'index.html')

def about(request):
    if request.user.is_authenticated:
        uid=request.user
        return redirect_based_on_user_type(request, request.user)
    return render(request,'about.html')

def contact(request):
    if request.user.is_authenticated:
        uid=request.user
        return redirect_based_on_user_type(request, request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        subjects = request.POST.get('subject')
        sender = request.POST.get('email')
        recipient = 'freelancehub76@gmail.com'
        message = request.POST.get('message')
        msg = message + '\n\n\nEmail : ' + sender
        from_email = name

        email = EmailMessage(
            subject=subjects,
            body=msg,
            from_email=from_email,
            to=[recipient],
            reply_to=[sender]
            )

        email.send(fail_silently=False)
        msg = "Thank you for contacting us. We will get back to you soon."
        return render(request, 'contact.html', {'msg': msg})
    return render(request, 'contact.html')

def service(request):
    if request.user.is_authenticated:
        uid=request.user
        return redirect_based_on_user_type(request, request.user)
    return render(request,'service.html')


def login_view(request):
    if request.user.is_authenticated and request.user.status=='active' :
        print(f"User {request.user} is already authenticated, redirecting...")
        return redirect_based_on_user_type(request, request.user)
    
    return render(request, 'login.html', {'page': 'sign-in'})



def register_view(request):
    if request.user.is_authenticated:
        print(f"User {request.user} is already authenticated, redirecting...")
        return redirect_based_on_user_type(request, request.user)
    print("Rendering register page")
    return render(request, 'login.html', {'page': 'sign-up'})

def faqs(request):
    if request.user.is_authenticated:
        uid=request.user
        return redirect_based_on_user_type(request, request.user)
    return render(request,'faqs.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pass')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            if not user.welcome_email_sent:
                user.welcome_email_sent = True
                user.save()
                
                send_welcome_email(request, user)
                
            return redirect_based_on_user_type(request, user)
        
        else:
            return render(request, 'login.html', {'error_msg': 'Invalid credentials', 'page': 'sign-in'})
    
    elif request.user.is_authenticated:
        user = request.user
        user.email_verified = True
        user.google = True
        user.save()
        
        if not user.welcome_email_sent:
            user.welcome_email_sent = True
            user.save()
            send_welcome_email(request, user)
                
        return redirect_based_on_user_type(request, user)
    
    url_parts = urlparse(request.get_full_path())
    query = parse_qs(url_parts.query)
    if 'next' in query:
        query.pop('next')
        url_parts = url_parts._replace(query=urlencode(query, doseq=True))
        clean_url = urlunparse(url_parts)
        return HttpResponseRedirect(clean_url)
    
    return render(request, 'login.html', {'page': 'sign-in'})



def redirect_based_on_user_type(request, user):
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    print(f"Redirecting user: {user}")
    
    existing_entry = Register.objects.filter(user_id=user.id).first()
    if not existing_entry:
        user2 = Register(first_name='', last_name='', user_id=user.id)
        user2.save()
        print(f"Created Register entry for user: {user}")
    
    print(f"User role: {user.role}")
    if not user.role:
        print(f"User role not set, redirecting to add_user_type for user: {user}")
        return add_user_type(request, user.id)
    
    if user.status != 'active':
        print(f"User status is not active, logging out user: {user}")
        return redirect('logout')
    
    
    if user.role == 'admin':
        auth_login(request, user)
        request.session['uid'] = user.id
        print(f"Redirecting admin user: {user}")
        return redirect('administrator:admin_view')
    elif user.role == 'client':
        auth_login(request, user)
        request.session['uid'] = user.id
        print(f"Redirecting client user: {user}")
        return redirect('client:client_view')
    elif user.role == 'freelancer':
        auth_login(request, user)
        request.session['uid'] = user.id
        print(f"Redirecting freelancer user: {user}")
        return redirect('freelancer:freelancer_view')
    else:
        print(f"User role is undefined, redirecting to login for user: {user}")
        return redirect('login')




def register(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if CustomUser.objects.filter(username=fname).exists() or CustomUser.objects.filter(email=email).exists():
            return render(request, 'login.html', {'page':'sign-up','error_msg': 'User with this name or email already exists'})
        else:
            user_type=''
            user = CustomUser.objects.create_user(username=fname,email=email, password=password,role=user_type)
            user.role = user_type
            user.save()
            
            uid=user.id
            reg=Register.objects.create(user_id=uid,first_name=fname,last_name=lname)
            reg.save()
            return render(request, 'register.html', {'user': user, 'uid': user.id})
        
            
    else:
        return redirect(register_view)



def add_user_type(request,uid):
    
    user = CustomUser.objects.get(id=uid)
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        user.role=user_type
        user.save()
        return redirect(login)
    return render(request, 'register.html', {'uid': uid,'user':user})
    
    

def send_welcome_email(request,user):
    subject = 'Welcome to FreelanceHub'
    context = {
        'user': user
    }
    html_content = render_to_string('welcome.html', context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()
    



def logout(request):
    auth_logout(request)
    for key in list(request.session.keys()):
        del request.session[key]
    return HttpResponseRedirect(reverse('login'))





def send_forget_password_mail(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            token = str(uuid.uuid4())
            msg = f'http://127.0.0.1:8000/reset_password/{token}/'
            context = {
                'user': user,
                'reset_link': msg
            }
            html_content = render_to_string('forgot_password.html', context)
            text_content = strip_tags(html_content)
            email = EmailMultiAlternatives('Password Reset', text_content, settings.EMAIL_HOST_USER, [user.email])
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            data = PasswordReset.objects.create(user_id=user, token=token)
            return redirect('login_view')
        except CustomUser.DoesNotExist:
            return render(request, 'mail_read.html', {'error': 'User with this email does not exist'})

    return render(request, 'mail_read.html')


def reset_password(request, token):
    reset_user = PasswordReset.objects.filter(token=token).first()

    if reset_user is None:
        return render(request, 'password_reset.html', {'message': 'Invalid or expired token'})

    uid = reset_user.user_id.id

    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        user_id = request.POST.get('user_id')

        if user_id is None:
            return render(request, 'password_reset.html', {'message': 'No user found'})

        if new_password != confirm_password:
            return render(request, 'password_reset.html', {'error': 'Passwords do not match'})

        user_obj = CustomUser.objects.get(id=user_id)
        user_obj.set_password(new_password)
        user_obj.save()
        
        return redirect('login_view')

    return render(request, 'password_reset.html', {'user_id': uid})


def send_verification_mail(request):
    email = request.user.email
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('login_view')

    token = str(uuid.uuid4())
    
    verification_link = f'http://127.0.0.1:8000/email_verification/{token}/'
    context = {
        'user': user,
        'reset_link': verification_link,
        
    }
    
    html_content = render_to_string('mail_send.html', context)
    text_content = strip_tags(html_content)
 
    email_msg = EmailMultiAlternatives('Email Verification', text_content, settings.EMAIL_HOST_USER, [user.email])
    email_msg.attach_alternative(html_content, "text/html")
    email_msg.send()
    
    EmailVerification.objects.create(user_id=user, token=token)

    
    messages.success(request, 'Verification email sent. Please check your inbox.')
    
    return redirect('login_view')



def email_verification(request, token):
    verification = EmailVerification.objects.filter(token=token).first()
    uid=verification.user_id_id
    if not verification:
        print(request, 'Invalid or expired token.')
        return redirect('login_view')
    user = CustomUser.objects.get(id=uid) 
    user.email_verified = True
    user.save()
    verification.delete()

    print( 'Email verified successfully.')

    return render(request,'email_verification.html')
